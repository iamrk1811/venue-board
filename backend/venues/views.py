from rest_framework.generics import ListAPIView
from .models import Venue
from .serializers import VenueSerializer


class VenueListView(ListAPIView):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
