from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer


@shared_task
def process_transaction(txn_id: str) -> None:
    """
    Update metrics, run anomaly detection, refresh the summary cache,
    and push the result to all connected dashboard clients in one shot.
    """
    from core.cache import accumulate_summary
    from metrics.services import AnomalyService, MetricsService
    from transactions.models import Transaction

    txn = Transaction.objects.prefetch_related("items").get(pk=txn_id)

    MetricsService.update_on_transaction(txn)
    AnomalyService.check(txn.venue_id)

    summary = accumulate_summary(txn)

    async_to_sync(get_channel_layer().group_send)(
        "dashboard",
        {
            "type": "summary_updated",
            "summary": summary,
            "venue_id": txn.venue_id,
        },
    )
