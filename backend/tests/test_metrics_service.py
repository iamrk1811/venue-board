import pytest
from decimal import Decimal

from django.utils import timezone

from core.utils import truncate_to_hour
from metrics.models import VenueDailySummary, VenueHourlyMetrics, VenueItemDaily
from metrics.services import MetricsService
from transactions.const import TransactionTypes


@pytest.mark.django_db
class TestMetricsServiceSale:
    def test_sale_increments_hourly_sales_and_transaction_count(self, venue, make_txn):
        txn = make_txn(venue.id, TransactionTypes.SALE, "150.00")
        txn.timestamp = timezone.now()
        MetricsService.update_on_transaction(txn)

        hour = truncate_to_hour(txn.timestamp)
        row = VenueHourlyMetrics.objects.get(venue_id=venue.id, hour=hour)
        assert row.total_sales == Decimal("150.00")
        assert row.transaction_count == 1
        assert row.void_count == 0

    def test_sale_increments_daily_sales_and_transaction_count(self, venue, make_txn):
        txn = make_txn(venue.id, TransactionTypes.SALE, "200.00")
        txn.timestamp = timezone.now()
        MetricsService.update_on_transaction(txn)

        row = VenueDailySummary.objects.get(venue_id=venue.id, date=txn.timestamp.date())
        assert row.total_sales == Decimal("200.00")
        assert row.transaction_count == 1

    def test_repeated_sales_accumulate_correctly(self, venue, make_txn):
        for amount in ("100.00", "250.00", "50.00"):
            txn = make_txn(venue.id, TransactionTypes.SALE, amount)
            txn.timestamp = timezone.now()
            MetricsService.update_on_transaction(txn)

        daily = VenueDailySummary.objects.get(venue_id=venue.id)
        assert daily.total_sales == Decimal("400.00")
        assert daily.transaction_count == 3

    def test_sale_creates_item_daily_record(self, venue, make_txn):
        txn = make_txn(
            venue.id, TransactionTypes.SALE, "25.00",
            items=[("chai-01", "Masala Chai", 2, "12.50")],
        )
        txn.timestamp = timezone.now()
        MetricsService.update_on_transaction(txn)

        item = VenueItemDaily.objects.get(venue_id=venue.id, item_id="chai-01")
        assert item.total_qty == 2
        assert item.total_revenue == Decimal("25.00")

    def test_repeated_sales_of_same_item_accumulate(self, venue, make_txn):
        for _ in range(3):
            txn = make_txn(
                venue.id, TransactionTypes.SALE, "12.50",
                items=[("chai-01", "Masala Chai", 1, "12.50")],
            )
            txn.timestamp = timezone.now()
            MetricsService.update_on_transaction(txn)

        item = VenueItemDaily.objects.get(venue_id=venue.id, item_id="chai-01")
        assert item.total_qty == 3
        assert item.total_revenue == Decimal("37.50")


@pytest.mark.django_db
class TestMetricsServiceVoid:
    def test_void_does_not_add_to_sales(self, venue, make_txn):
        txn = make_txn(venue.id, TransactionTypes.VOID, "0.00")
        txn.timestamp = timezone.now()
        MetricsService.update_on_transaction(txn)

        daily = VenueDailySummary.objects.get(venue_id=venue.id)
        assert daily.total_sales == Decimal("0.00")
        assert daily.void_count == 1
        assert daily.transaction_count == 1

    def test_void_does_not_create_item_records(self, venue, make_txn):
        txn = make_txn(
            venue.id, TransactionTypes.VOID, "0.00",
            items=[("chai-01", "Masala Chai", 2, "12.50")],
        )
        txn.timestamp = timezone.now()
        MetricsService.update_on_transaction(txn)

        assert not VenueItemDaily.objects.filter(venue_id=venue.id).exists()


@pytest.mark.django_db
class TestMetricsServiceRefund:
    def test_refund_does_not_add_to_sales(self, venue, make_txn):
        txn = make_txn(venue.id, TransactionTypes.REFUND, "0.00")
        txn.timestamp = timezone.now()
        MetricsService.update_on_transaction(txn)

        daily = VenueDailySummary.objects.get(venue_id=venue.id)
        assert daily.total_sales == Decimal("0.00")
        assert daily.refund_count == 1
        assert daily.void_count == 0
