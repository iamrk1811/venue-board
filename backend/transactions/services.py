from django.db import transaction as db_transaction
from venues.models import Venue
from .models import Transaction, TransactionItem


class TransactionService:
    @staticmethod
    def ingest(validated_data: dict) -> Transaction:
        venue = Venue.objects.get(pk=validated_data["venue_id"])
        txn = None
        with db_transaction.atomic():
            txn = Transaction.objects.create(
                venue=venue,
                type=validated_data["type"],
                total=validated_data["total"],
                staff_id=validated_data["staff_id"],
            )
            TransactionItem.objects.bulk_create([
                TransactionItem(
                    transaction=txn,
                    item_id=item["item_id"],
                    name=item["name"],
                    qty=item["qty"],
                    price=item["price"],
                )
                for item in validated_data.get("items", [])
            ])

        # Run metrics + anomaly detection outside the atomic block so a metrics
        # failure never rolls back the raw transaction record.
        from metrics.services import MetricsService, AnomalyService
        MetricsService.update_on_transaction(txn)
        # AnomalyService.check(txn.venue_id)

        # # Broadcast thin WebSocket event — just the venue_id, no full payload.
        # from channels.layers import get_channel_layer
        # from asgiref.sync import async_to_sync
        # channel_layer = get_channel_layer()
        # async_to_sync(channel_layer.group_send)(
        #     "dashboard",
        #     {
        #         "type": "venue.metrics.updated",
        #         "venue_id": txn.venue_id,
        #     },
        # )

        return txn
