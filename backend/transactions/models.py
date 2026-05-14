import uuid

from django.db import models
from django.utils import timezone

from core.models import TimeStampedModel
from venues.models import Venue
from .const import TransactionTypes


class Transaction(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="transactions")
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)  # POS-issued time; used for metric bucketing
    type = models.IntegerField(choices=TransactionTypes.TYPES, db_index=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    staff_id = models.CharField(max_length=100)

    class Meta:
        indexes = [
            models.Index(fields=["venue", "timestamp"]),
            models.Index(fields=["type", "timestamp"]),
        ]
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.id} ({self.type})"


class TransactionItem(TimeStampedModel):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="items")
    item_id = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    qty = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        indexes = [
            models.Index(fields=["transaction"]),
        ]
