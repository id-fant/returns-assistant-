from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import ReturnRequest
from .serializers import ReturnRequestSerializer
from .ai_engine import get_return_decision


class ReturnRequestListView(APIView):
    """
    GET  /api/returns/     → List all return requests
    POST /api/returns/     → Submit a new return request (triggers AI decision)

    APIView is the base class in DRF. We override get() and post()
    to handle the two HTTP methods separately.
    """

    def get(self, request):
        """Return all stored return requests, newest first."""
        all_returns = ReturnRequest.objects.all()
        serializer = ReturnRequestSerializer(all_returns, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Accept a new return request, run it through the AI engine,
        attach the decision, then save and return the full record.
        """
        serializer = ReturnRequestSerializer(data=request.data)

        if not serializer.is_valid():
            # Return validation errors (e.g. missing fields) as 400
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Extract the fields we need for the AI prompt
        product = serializer.validated_data['product_name']
        reason = serializer.validated_data['reason']

        # Call Gemini — this returns (decision_string, explanation_string)
        decision, explanation = get_return_decision(product, reason)

        # Save the record with AI fields attached
        instance = serializer.save(
            ai_decision=decision,
            ai_explanation=explanation
        )

        return Response(
            ReturnRequestSerializer(instance).data,
            status=status.HTTP_201_CREATED
        )


class ReturnRequestDetailView(APIView):
    """
    GET /api/returns/<id>/  → Fetch a single return request by ID
    """

    def get(self, request, pk):
        try:
            return_request = ReturnRequest.objects.get(pk=pk)
        except ReturnRequest.DoesNotExist:
            return Response(
                {'error': f'Return request with id {pk} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ReturnRequestSerializer(return_request)
        return Response(serializer.data)
