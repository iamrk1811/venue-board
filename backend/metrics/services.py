from datetime import timedelta
from decimal import Decimal

from django.db import transaction as db_transaction
from django.db.models import F
from django.utils import timezone

from .models import VenueHourlyMetrics, VenueDailySummary, VenueItemDaily, Alert
from transactions.const import TransactionTypes
from core.utils import truncate_to_hour
from decouple import config
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class MetricsService:
    @staticmethod
    def update_on_transaction(txn) -> None:
        hour = truncate_to_hour(txn.created_at)
        date = txn.created_at.date()

        is_sale = txn.type == TransactionTypes.SALE
        is_void = txn.type == TransactionTypes.VOID
        is_refund = txn.type == TransactionTypes.REFUND

        sale_amount = txn.total if is_sale else Decimal("0")

        with db_transaction.atomic():
            # Hourly, ensure row exists, then atomically increment
            VenueHourlyMetrics.objects.get_or_create(
                venue_id=txn.venue_id,
                hour=hour,
                defaults={
                    "total_sales": Decimal("0"),
                    "transaction_count": 0,
                    "void_count": 0,
                    "refund_count": 0,
                },
            )
            VenueHourlyMetrics.objects.filter(venue_id=txn.venue_id, hour=hour).update(
                total_sales=F("total_sales") + sale_amount,
                transaction_count=F("transaction_count") + 1,
                void_count=F("void_count") + (1 if is_void else 0),
                refund_count=F("refund_count") + (1 if is_refund else 0),
            )

            # Daily
            VenueDailySummary.objects.get_or_create(
                venue_id=txn.venue_id,
                date=date,
                defaults={
                    "total_sales": Decimal("0"),
                    "transaction_count": 0,
                    "void_count": 0,
                    "refund_count": 0,
                },
            )
            VenueDailySummary.objects.filter(venue_id=txn.venue_id, date=date).update(
                total_sales=F("total_sales") + sale_amount,
                transaction_count=F("transaction_count") + 1,
                void_count=F("void_count") + (1 if is_void else 0),
                refund_count=F("refund_count") + (1 if is_refund else 0),
            )

            # Item aggregates for sales only
            if is_sale:
                for item in txn.items.all():
                    VenueItemDaily.objects.get_or_create(
                        venue_id=txn.venue_id,
                        date=date,
                        item_id=item.item_id,
                        defaults={
                            "item_name": item.name,
                            "total_qty": 0,
                            "total_revenue": Decimal("0"),
                        },
                    )
                    VenueItemDaily.objects.filter(
                        venue_id=txn.venue_id, date=date, item_id=item.item_id
                    ).update(
                        item_name=item.name,
                        total_qty=F("total_qty") + item.qty,
                        total_revenue=F("total_revenue") + (item.price * item.qty),
                    )


class AnomalyService:
    @staticmethod
    def check(venue_id: int) -> None:
        AnomalyService._check_sales_drop(venue_id)
        AnomalyService._check_void_spike(venue_id)

    @staticmethod
    def _check_sales_drop(venue_id: int) -> None:
        now = timezone.now()
        current_hour = truncate_to_hour(now)
        prev_hour = current_hour - timedelta(hours=1)

        try:
            current = VenueHourlyMetrics.objects.get(venue_id=venue_id, hour=current_hour)
            previous = VenueHourlyMetrics.objects.get(venue_id=venue_id, hour=prev_hour)
        except VenueHourlyMetrics.DoesNotExist:
            return

        if previous.total_sales <= 0:
            return

        drop_percent = float(previous.total_sales - current.total_sales) / float(previous.total_sales)

        sale_drop_warning_threshold = config("SALES_DROP_PERCENT", cast=float, default=0.40)
        sale_drop_critical_threshold = config("SALES_DROP_CRITICAL_THRESHOLD", cast=float, default=0.70)

        if drop_percent >= sale_drop_warning_threshold:
            severity = "critical" if drop_percent >= sale_drop_critical_threshold else "warning"
            alert, created = Alert.objects.get_or_create(
                venue_id=venue_id,
                type="sales_drop",
                is_active=True,
                defaults={
                    "severity": severity,
                    "message": (
                        f"Sales dropped {drop_percent:.0%} vs previous hour "
                        f"(${current.total_sales:.2f} vs ${previous.total_sales:.2f})"
                    ),
                },
            )
            if created:
                AnomalyService._broadcast_alert(alert)
        else:
            # Resolve existing alert if sales have recovered
            Alert.objects.filter(venue_id=venue_id, type="sales_drop", is_active=True).update(
                is_active=False,
                resolved_at=now,
            )

    @staticmethod
    def _check_void_spike(venue_id: int) -> None:
        now = timezone.now()
        current_hour = truncate_to_hour(now)
        seven_days_ago = current_hour - timedelta(days=7)

        try:
            current = VenueHourlyMetrics.objects.get(venue_id=venue_id, hour=current_hour)
        except VenueHourlyMetrics.DoesNotExist:
            return

        if current.transaction_count < 5:
            return

        current_void_rate = current.void_count / current.transaction_count

        # Baseline: avg void rate at the same hour-of-day over the past 7 days
        baseline_qs = VenueHourlyMetrics.objects.filter(
            venue_id=venue_id,
            hour__gte=seven_days_ago,
            hour__lt=current_hour,
            hour__hour=current_hour.hour,
            transaction_count__gt=0,
        )
        if not baseline_qs.exists():
            return

        total_voids = sum(m.void_count for m in baseline_qs)
        total_txns = sum(m.transaction_count for m in baseline_qs)
        baseline_rate = total_voids / total_txns if total_txns > 0 else 0

        if baseline_rate > 0 and current_void_rate > baseline_rate * 2.0:
            alert, created = Alert.objects.get_or_create(
                venue_id=venue_id,
                type="void_spike",
                is_active=True,
                defaults={
                    "severity": "warning",
                    "message": (
                        f"Void rate {current_void_rate:.0%} is 2x above the 7-day baseline "
                        f"({baseline_rate:.0%}) for this hour"
                    ),
                },
            )
            if created:
                AnomalyService._broadcast_alert(alert)

    @staticmethod
    def _broadcast_alert(alert: Alert) -> None:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "dashboard",
            {
                "type": "alert.triggered",
                "alert": {
                    "id": alert.id,
                    "venue_id": alert.venue_id,
                    "alert_type": alert.type,
                    "severity": alert.severity,
                    "message": alert.message,
                    "created_at": alert.created_at.isoformat(),
                },
            },
        )
