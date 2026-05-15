import pytest
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.utils import timezone

from core.utils import truncate_to_hour
from metrics.models import Alert, VenueHourlyMetrics
from metrics.services import AnomalyService


def make_hourly(venue_id, hour, total_sales, txn_count=10, void_count=0):
    return VenueHourlyMetrics.objects.create(
        venue_id=venue_id,
        hour=hour,
        total_sales=Decimal(str(total_sales)),
        transaction_count=txn_count,
        void_count=void_count,
        refund_count=0,
    )


def run_sales_drop_check(venue_id, fixed_now):
    with patch("django.utils.timezone.now", return_value=fixed_now), \
         patch.object(AnomalyService, "_broadcast_alert"):
        AnomalyService._check_sales_drop(venue_id)


def run_void_spike_check(venue_id, fixed_now):
    with patch("django.utils.timezone.now", return_value=fixed_now), \
         patch.object(AnomalyService, "_broadcast_alert"):
        AnomalyService._check_void_spike(venue_id)


@pytest.mark.django_db
class TestSalesDropDetection:
    def test_creates_warning_alert_on_drop_between_40_and_70_percent(self, venue):
        now = timezone.now()
        current_hour = truncate_to_hour(now)
        make_hourly(venue.id, current_hour - timedelta(hours=1), "1000.00")
        make_hourly(venue.id, current_hour, "500.00")  # 50% drop

        run_sales_drop_check(venue.id, now)

        alert = Alert.objects.get(venue_id=venue.id, type="sales_drop")
        assert alert.is_active
        assert alert.severity == "warning"

    def test_creates_critical_alert_on_drop_above_70_percent(self, venue):
        now = timezone.now()
        current_hour = truncate_to_hour(now)
        make_hourly(venue.id, current_hour - timedelta(hours=1), "1000.00")
        make_hourly(venue.id, current_hour, "200.00")  # 80% drop

        run_sales_drop_check(venue.id, now)

        alert = Alert.objects.get(venue_id=venue.id, type="sales_drop")
        assert alert.severity == "critical"

    def test_resolves_existing_alert_when_sales_recover(self, venue):
        now = timezone.now()
        current_hour = truncate_to_hour(now)
        Alert.objects.create(
            venue=venue, type="sales_drop",
            severity="warning", message="drop", is_active=True,
        )
        make_hourly(venue.id, current_hour - timedelta(hours=1), "1000.00")
        make_hourly(venue.id, current_hour, "970.00")  # 3% drop — below threshold

        run_sales_drop_check(venue.id, now)

        alert = Alert.objects.get(venue_id=venue.id, type="sales_drop")
        assert not alert.is_active
        assert alert.resolved_at is not None

    def test_no_alert_when_previous_hour_has_no_data(self, venue):
        now = timezone.now()
        current_hour = truncate_to_hour(now)
        make_hourly(venue.id, current_hour, "500.00")
        # no previous hour row

        run_sales_drop_check(venue.id, now)

        assert not Alert.objects.filter(venue_id=venue.id).exists()

    def test_does_not_create_duplicate_alert_if_one_already_active(self, venue):
        now = timezone.now()
        current_hour = truncate_to_hour(now)
        existing = Alert.objects.create(
            venue=venue, type="sales_drop",
            severity="warning", message="existing", is_active=True,
        )
        make_hourly(venue.id, current_hour - timedelta(hours=1), "1000.00")
        make_hourly(venue.id, current_hour, "500.00")

        run_sales_drop_check(venue.id, now)

        assert Alert.objects.filter(venue_id=venue.id, type="sales_drop", is_active=True).count() == 1
        assert Alert.objects.get(venue_id=venue.id, type="sales_drop", is_active=True).id == existing.id


@pytest.mark.django_db
class TestVoidSpikeDetection:
    def test_creates_alert_when_void_rate_exceeds_2x_baseline(self, venue):
        now = timezone.now()
        current_hour = truncate_to_hour(now)
        yesterday_same_hour = current_hour - timedelta(days=1)

        # base: 10% void rate (1 void / 10 txns)
        make_hourly(venue.id, yesterday_same_hour, "500.00", txn_count=10, void_count=1)
        # current: 40% void rate (4 voids / 10 txns)
        make_hourly(venue.id, current_hour, "500.00", txn_count=10, void_count=4)

        run_void_spike_check(venue.id, now)

        assert Alert.objects.filter(venue_id=venue.id, type="void_spike", is_active=True).exists()

    def test_no_alert_when_no_baseline_history_exists(self, venue):
        now = timezone.now()
        current_hour = truncate_to_hour(now)
        # High void rate but zero baseline data — cannot determine anomaly
        make_hourly(venue.id, current_hour, "500.00", txn_count=10, void_count=8)

        run_void_spike_check(venue.id, now)

        assert not Alert.objects.filter(venue_id=venue.id, type="void_spike").exists()
