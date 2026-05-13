from rest_framework import serializers
from .const import TransactionTypes
from venues.models import Venue

class TransactionItemSerializer(serializers.Serializer):
    item_id = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=200)
    qty = serializers.IntegerField(min_value=1)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)


class TransactionIngestSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    venue_id = serializers.IntegerField()
    created_at = serializers.DateTimeField(read_only=True)
    type = serializers.ChoiceField(choices=[TransactionTypes.SALE, TransactionTypes.VOID, TransactionTypes.REFUND])
    items = TransactionItemSerializer(many=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    staff_id = serializers.CharField(max_length=100)

    def validate_venue_id(self, value):
        try:
            Venue.objects.get(id=value)
        except Venue.DoesNotExist:
            raise serializers.ValidationError("Invalid venue_id")
        return value
