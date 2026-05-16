import logging
from decimal import Decimal

from django.core.cache import cache
from django.db.models import Sum
from django.utils import timezone

from metrics.models import Alert, VenueDailySummary, VenueItemDaily
from metrics.serializers import VenueRankingSerializer
from transactions.const import TransactionTypes

logger = logging.getLogger(__name__)

SUMMARY_TTL = 900  # 15 min safety-net rebuild


def _summary_key():
    return f"dashboard:summary:{timezone.now().date()}"


def build_summary() -> dict:
    """Compute the dashboard summary from the DB. Always reads fresh data."""
    today = timezone.now().date()
    logger.info("building summary from db for date=%s", today)

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


def _accumulate_summary(cached_summary: dict, txn) -> dict | None:
    """
    accumalate with time on each transaction to avoid fetching/calculation and returns updated summary
    """
    is_sale = txn.type == TransactionTypes.SALE
    is_void = txn.type == TransactionTypes.VOID
    is_refund = txn.type == TransactionTypes.REFUND
    sale_amount = txn.total if is_sale else Decimal("0")

    # global counters
    total_sales = Decimal(cached_summary["total_sales_today"]) + sale_amount
    total_transactions = cached_summary["total_transactions_today"] + 1

    # venue rankings: find this venue and update, re-sort
    rankings = [dict(r) for r in cached_summary["venue_rankings"]]
    venue_entry = next((v for v in rankings if v["venue_id"] == txn.venue_id), None)
    if venue_entry is None:
        # new venue appearing for the first time today, need a full rebuild.
        return None

    venue_entry["total_sales"] = str(Decimal(venue_entry["total_sales"]) + sale_amount)
    venue_entry["transaction_count"] += 1
    if is_void:
        venue_entry["void_count"] += 1
    if is_refund:
        venue_entry["refund_count"] += 1

    rankings.sort(key=lambda v: Decimal(v["total_sales"]), reverse=True)

    #  alert count: AnomalyService may have resolved/created alerts
    active_alert_count = Alert.objects.filter(is_active=True).count()

    #  top items: accumulate for sales only
    top_items = [dict(i) for i in cached_summary["top_items"]]
    if is_sale:
        top_item_ids = {item["item_id"] for item in top_items}
        unknown_item_ids = []

        for txn_item in txn.items.all():
            if txn_item.item_id in top_item_ids:
                entry = next(i for i in top_items if i["item_id"] == txn_item.item_id)
                entry["total_qty"] += txn_item.qty
                entry["total_revenue"] = str(
                    Decimal(entry["total_revenue"]) + txn_item.price * txn_item.qty
                )
            else:
                unknown_item_ids.append(txn_item.item_id)

        if unknown_item_ids:
            today = timezone.now().date()
            new_aggregates = list(
                VenueItemDaily.objects
                .filter(date=today, item_id__in=unknown_item_ids)
                .values("item_id", "item_name")
                .annotate(total_qty=Sum("total_qty"), total_revenue=Sum("total_revenue"))
            )
            for item in new_aggregates:
                top_items.append({
                    "item_id": item["item_id"],
                    "item_name": item["item_name"],
                    "total_qty": item["total_qty"],
                    "total_revenue": str(item["total_revenue"]),
                })

        top_items.sort(key=lambda i: Decimal(i["total_revenue"]), reverse=True)
        top_items = top_items[:10]

    return {
        "total_sales_today": str(total_sales),
        "total_transactions_today": total_transactions,
        "active_alert_count": active_alert_count,
        "venue_rankings": rankings,
        "top_items": top_items,
    }


def get_summary() -> dict:
    """Return cached summary or compute and cache it on miss"""
    key = _summary_key()
    data = cache.get(key)
    if data is None:
        data = build_summary()
        cache.set(key, data, SUMMARY_TTL)
    return data


def accumulate_summary(txn) -> dict:
    """
    Update the cached summary by accumulating the transaction.
    Falls back to a full build_summary() on cache miss
    """
    key = _summary_key()
    cached_summary = cache.get(key)
    if cached_summary is not None:
        data = _accumulate_summary(cached_summary, txn)
        if data is not None:
            cache.set(key, data, SUMMARY_TTL)
            return data
    logger.warning("summary cache miss for txn_id=%s, falling back to full rebuild", txn.id)
    data = build_summary()
    cache.set(key, data, SUMMARY_TTL)
    return data
