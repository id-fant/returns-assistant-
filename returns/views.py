from rest_framework import generics

from .ai_engine import get_return_decision
from .models import ReturnRequest
from .serializers import ReturnRequestSerializer


class ReturnRequestListView(generics.ListCreateAPIView):
    """
    GET  /api/returns/   → List all return requests (newest first via Meta.ordering)
    POST /api/returns/   → Create a return request; AI decision is attached server-side
    """

    queryset = ReturnRequest.objects.all()
    serializer_class = ReturnRequestSerializer

    def perform_create(self, serializer):
        product = serializer.validated_data["product_name"]
        reason = serializer.validated_data["reason"]
        decision, explanation = get_return_decision(product, reason)
        serializer.save(ai_decision=decision, ai_explanation=explanation)


class ReturnRequestDetailView(generics.RetrieveAPIView):
    """GET /api/returns/<id>/ → Fetch a single return request."""

    queryset = ReturnRequest.objects.all()
    serializer_class = ReturnRequestSerializer
