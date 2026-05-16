import pytest
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.utils import timezone

from core.utils import truncate_to_hour
from metrics.models import Alert, VenueHourlyMetrics
from metrics.services import AnomalyService


def make_hourly(venue_id, hour, total_sales, txn_count=10, void_count=0, refund_count=0):
    return VenueHourlyMetrics.objects.create(
        venue_id=venue_id,
        hour=hour,
        total_sales=Decimal(str(total_sales)),
        transaction_count=txn_count,
        void_count=void_count,
        refund_count=refund_count,
    )


def run_check(venue_id, fixed_now):
    with patch("django.utils.timezone.now", return_value=fixed_now), \
         patch.object(AnomalyService, "_broadcast_alert"):
        AnomalyService.check(venue_id)


@pytest.mark.django_db
class TestSalesDropDetection:
    def test_creates_alert_on_significant_drop(self, venue):
        now = timezone.now()
        current_hour = truncate_to_hour(now)
        make_hourly(venue.id, current_hour - timedelta(hours=1), "1000.00")
        make_hourly(venue.id, current_hour, "500.00")  # 50% drop

        run_check(venue.id, now)

        assert Alert.objects.filter(venue_id=venue.id, type="sales_drop", is_active=True).exists()

    def test_resolves_alert_when_sales_recover(self, venue):
        now = timezone.now()
        current_hour = truncate_to_hour(now)
        Alert.objects.create(venue=venue, type="sales_drop", severity="warning", message="drop", is_active=True)
        make_hourly(venue.id, current_hour - timedelta(hours=1), "1000.00")
        make_hourly(venue.id, current_hour, "970.00")  # 3% drop — below threshold

        run_check(venue.id, now)

        alert = Alert.objects.get(venue_id=venue.id, type="sales_drop")
        assert not alert.is_active
        assert alert.resolved_at is not None

    def test_no_alert_without_previous_hour_data(self, venue):
        now = timezone.now()
        make_hourly(venue.id, truncate_to_hour(now), "500.00")

        run_check(venue.id, now)

        assert not Alert.objects.filter(venue_id=venue.id).exists()


@pytest.mark.django_db
class TestVoidSpikeDetection:
    def test_creates_alert_on_significant_spike(self, venue):
        now = timezone.now()
        current_hour = truncate_to_hour(now)
        # 10% → 30%: 200% increase, triggers critical
        make_hourly(venue.id, current_hour - timedelta(hours=1), "500.00", txn_count=10, void_count=1)
        make_hourly(venue.id, current_hour, "500.00", txn_count=10, void_count=3)

        run_check(venue.id, now)

        assert Alert.objects.filter(venue_id=venue.id, type="void_spike", is_active=True).exists()

    def test_resolves_alert_when_void_rate_recovers(self, venue):
        now = timezone.now()
        current_hour = truncate_to_hour(now)
        Alert.objects.create(venue=venue, type="void_spike", severity="warning", message="spike", is_active=True)
        make_hourly(venue.id, current_hour - timedelta(hours=1), "500.00", txn_count=10, void_count=2)
        make_hourly(venue.id, current_hour, "500.00", txn_count=10, void_count=2)  # 0% increase

        run_check(venue.id, now)

        alert = Alert.objects.get(venue_id=venue.id, type="void_spike")
        assert not alert.is_active
        assert alert.resolved_at is not None

    def test_no_alert_without_previous_hour_data(self, venue):
        now = timezone.now()
        make_hourly(venue.id, truncate_to_hour(now), "500.00", txn_count=10, void_count=8)

        run_check(venue.id, now)

        assert not Alert.objects.filter(venue_id=venue.id, type="void_spike").exists()


@pytest.mark.django_db
class TestRefundSpikeDetection:
    def test_creates_alert_on_significant_spike(self, venue):
        now = timezone.now()
        current_hour = truncate_to_hour(now)
        # 10% → 30%: 200% increase, triggers critical
        make_hourly(venue.id, current_hour - timedelta(hours=1), "500.00", txn_count=10, refund_count=1)
        make_hourly(venue.id, current_hour, "500.00", txn_count=10, refund_count=3)

        run_check(venue.id, now)

        assert Alert.objects.filter(venue_id=venue.id, type="refund_spike", is_active=True).exists()

    def test_resolves_alert_when_refund_rate_recovers(self, venue):
        now = timezone.now()
        current_hour = truncate_to_hour(now)
        Alert.objects.create(venue=venue, type="refund_spike", severity="warning", message="spike", is_active=True)
        make_hourly(venue.id, current_hour - timedelta(hours=1), "500.00", txn_count=10, refund_count=2)
        make_hourly(venue.id, current_hour, "500.00", txn_count=10, refund_count=2)  # 0% increase

        run_check(venue.id, now)

        alert = Alert.objects.get(venue_id=venue.id, type="refund_spike")
        assert not alert.is_active
        assert alert.resolved_at is not None

    def test_no_alert_without_previous_hour_data(self, venue):
        now = timezone.now()
        make_hourly(venue.id, truncate_to_hour(now), "500.00", txn_count=10, refund_count=8)

        run_check(venue.id, now)

        assert not Alert.objects.filter(venue_id=venue.id, type="refund_spike").exists()
