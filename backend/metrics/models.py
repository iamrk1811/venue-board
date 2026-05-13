from django.db import models

from core.models import TimeStampedModel
from venues.models import Venue


class VenueHourlyMetrics(TimeStampedModel):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="hourly_metrics")
    hour = models.DateTimeField()
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transaction_count = models.IntegerField(default=0)
    void_count = models.IntegerField(default=0)
    refund_count = models.IntegerField(default=0)

    class Meta:
        unique_together = [("venue", "hour")]
        indexes = [
            models.Index(fields=["venue", "hour"]),
            models.Index(fields=["hour"]),
        ]
        ordering = ["hour"]

    def __str__(self):
        return f"{self.venue} @ {self.hour}"


class VenueDailySummary(TimeStampedModel):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="daily_summaries")
    date = models.DateField()
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transaction_count = models.IntegerField(default=0)
    void_count = models.IntegerField(default=0)
    refund_count = models.IntegerField(default=0)

    class Meta:
        unique_together = [("venue", "date")]
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["date", "total_sales"]),
        ]
        ordering = ["-total_sales"]

    def __str__(self):
        return f"{self.venue} on {self.date}"


class VenueItemDaily(TimeStampedModel):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="item_daily")
    date = models.DateField()
    item_id = models.CharField(max_length=100)
    item_name = models.CharField(max_length=200)
    total_qty = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        unique_together = [("venue", "date", "item_id")]
        indexes = [
            models.Index(fields=["date", "total_revenue"]),
            models.Index(fields=["venue", "date", "total_revenue"]),
        ]


class Alert(TimeStampedModel):
    ALERT_TYPES = [
        ("sales_drop", "Sales Drop"),
        ("void_spike", "Void Spike"),
        ("refund_spike", "Refund Spike"),
    ]
    SEVERITY = [
        ("warning", "Warning"),
        ("critical", "Critical"),
    ]

    venue = models.ForeignKey(
        Venue, on_delete=models.CASCADE, related_name="alerts", null=True, blank=True
    )
    type = models.CharField(max_length=50, choices=ALERT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY, default="warning")
    message = models.TextField()
    is_active = models.BooleanField(default=True, db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["is_active", "-created_at"]),
            models.Index(fields=["venue", "is_active"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.type} @ {self.venue} ({self.severity})"
