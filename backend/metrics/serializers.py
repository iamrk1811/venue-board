from rest_framework import serializers
from .models import VenueHourlyMetrics, VenueDailySummary, VenueItemDaily, Alert


class VenueRankingSerializer(serializers.ModelSerializer):
    venue_id = serializers.IntegerField()
    name = serializers.CharField(source="venue.name")

    class Meta:
        model = VenueDailySummary
        fields = ["venue_id", "name", "total_sales", "transaction_count", "void_count", "refund_count"]


class TopItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueItemDaily
        fields = ["item_id", "item_name", "total_qty", "total_revenue"]


class HourlyMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueHourlyMetrics
        fields = ["hour", "total_sales", "transaction_count", "void_count", "refund_count"]


class AlertSerializer(serializers.ModelSerializer):
    venue_name = serializers.SerializerMethodField()

    class Meta:
        model = Alert
        fields = ["id", "venue_id", "venue_name", "type", "severity", "message", "created_at"]

    def get_venue_name(self, obj):
        return obj.venue.name if obj.venue else None
