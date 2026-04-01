from rest_framework import serializers
from .models import ReturnRequest


class ReturnRequestSerializer(serializers.ModelSerializer):
    """
    ModelSerializer automatically generates fields from the model.
    read_only_fields means the client cannot set these — they are
    computed server-side (by the AI engine) and returned in the response.
    """

    class Meta:
        model = ReturnRequest
        fields = [
            'id',
            'order_id',
            'product_name',
            'reason',
            'ai_decision',
            'ai_explanation',
            'created_at',
        ]
        read_only_fields = ['id', 'ai_decision', 'ai_explanation', 'created_at']
