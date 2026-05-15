from rest_framework.generics import ListAPIView

from core.responses import success_response

from .models import Venue
from .serializers import VenueSerializer


class VenueListView(ListAPIView):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return success_response(response.data)
