from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.views import APIView

from core.responses import success_response

from .serializers import TransactionIngestSerializer
from .services import TransactionService


class TransactionIngestView(APIView):
    @extend_schema(
        tags=["transactions"],
        summary="Ingest a POS transaction",
        description="Accepts a single transaction from a venue POS system",
        request=TransactionIngestSerializer,
        responses={
            201: OpenApiResponse(description="Transaction accepted and metrics updated"),
            400: OpenApiResponse(description="Validation error / malformed payload"),
            401: OpenApiResponse(description="Missing or invalid JWT token"),
        }
    )
    def post(self, request):
        serializer = TransactionIngestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        TransactionService.ingest(serializer.validated_data)
        return success_response(None, status=201)
