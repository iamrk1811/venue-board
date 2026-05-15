from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


@shared_task
def update_metrics(txn_id: str) -> None:
    """
    Update hourly/daily metrics for a transaction
    """
    from transactions.models import Transaction
    from metrics.services import MetricsService
    from core.cache import refresh_summary

    txn = Transaction.objects.get(pk=txn_id)
    MetricsService.update_on_transaction(txn)

    summary = refresh_summary()

    async_to_sync(get_channel_layer().group_send)(
        "dashboard",
        {
            "type": "summary_updated",
            "summary": summary,
            "venue_id": txn.venue_id,
        },
    )


@shared_task
def check_anomaly(venue_id: int) -> None:
    """
    Run anomaly detection for a venue
    """
    from metrics.services import AnomalyService

    AnomalyService.check(venue_id)
