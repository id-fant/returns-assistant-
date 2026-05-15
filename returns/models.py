from django.db import models


class ReturnRequest(models.Model):
    """
    A single customer return request.

    The customer supplies order_id, product_name, and reason.
    The AI engine fills ai_decision and ai_explanation server-side
    before the row is persisted (see returns.views.ReturnRequestListView).
    """

    class Decision(models.TextChoices):
        APPROVE = "APPROVE", "Approve"
        EXCHANGE = "EXCHANGE", "Exchange"
        ESCALATE = "ESCALATE", "Escalate"
        PENDING = "PENDING", "Pending"

    order_id = models.CharField(max_length=100)
    product_name = models.CharField(max_length=255)
    reason = models.TextField()

    ai_decision = models.CharField(
        max_length=20,
        choices=Decision.choices,
        default=Decision.PENDING,
        blank=True,
    )
    ai_explanation = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.ai_decision}] {self.order_id} - {self.product_name}"
