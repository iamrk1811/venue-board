from django.db import transaction as db_transaction
from venues.models import Venue
from .models import Transaction, TransactionItem
from metrics.services import MetricsService, AnomalyService
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


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

        # store metrics and anomaly
        MetricsService.update_on_transaction(txn)
        AnomalyService.check(txn.venue_id)

        # broadcast the event
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "dashboard",
            {
                "type": "venue.metrics.updated",
                "venue_id": txn.venue_id,
            },
        )

        return txn
