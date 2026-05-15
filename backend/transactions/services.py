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
                timestamp=validated_data["timestamp"],
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

        if txn is None:
            # TODO handle failure
            return
        from metrics.tasks import process_transaction
        process_transaction.apply_async(args=[str(txn.id)], queue="metrics")

        return txn
