from django.core.cache import cache
from django.db.models import Sum
from django.utils import timezone

SUMMARY_TTL = 3600


def _summary_key():
    return f"dashboard:summary:{timezone.now().date()}"


def build_summary() -> dict:
    """Compute the dashboard summary from the DB. Always reads fresh data"""
    from metrics.models import Alert, VenueDailySummary, VenueItemDaily
    from metrics.serializers import VenueRankingSerializer

    today = timezone.now().date()

    summaries = (
        VenueDailySummary.objects
        .filter(date=today)
        .select_related("venue")
        .order_by("-total_sales")
    )

    total_sales = sum(s.total_sales for s in summaries)
    total_transactions = sum(s.transaction_count for s in summaries)
    active_alert_count = Alert.objects.filter(is_active=True).count()

    top_items = list(
        VenueItemDaily.objects
        .filter(date=today)
        .values("item_id", "item_name")
        .annotate(total_qty=Sum("total_qty"), total_revenue=Sum("total_revenue"))
        .order_by("-total_revenue")[:10]
    )

    return {
        "total_sales_today": str(total_sales),
        "total_transactions_today": total_transactions,
        "active_alert_count": active_alert_count,
        "venue_rankings": list(VenueRankingSerializer(summaries, many=True).data),
        "top_items": [
            {
                "item_id": item["item_id"],
                "item_name": item["item_name"],
                "total_qty": item["total_qty"],
                "total_revenue": str(item["total_revenue"]),
            }
            for item in top_items
        ],
    }


def get_summary() -> dict:
    """Return cached summary or compute and cache it on miss"""
    key = _summary_key()
    data = cache.get(key)
    if data is None:
        data = build_summary()
        cache.set(key, data, SUMMARY_TTL)
    return data


def refresh_summary() -> dict:
    """Force recompute summary, update cache return data"""
    data = build_summary()
    cache.set(_summary_key(), data, SUMMARY_TTL)
    return data
