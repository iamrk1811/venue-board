import logging

from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def process_transaction(self, txn_id: str) -> None:
    """
    Update metrics, run anomaly detection, refresh the summary cache,
    and push the result to all connected dashboard clients in one shot.
    """
    from core.cache import accumulate_summary
    from metrics.services import AnomalyService, MetricsService
    from transactions.models import Transaction

    try:
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
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            logger.error(
                "process_transaction failed permanently after %d retries for txn_id=%s: %s",
                self.max_retries,
                txn_id,
                exc,
                exc_info=True,
            )
            raise
        raise self.retry(exc=exc)
