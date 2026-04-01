from django.db import models


class ReturnRequest(models.Model):
    """
    Represents a single customer return request.
    Django automatically creates an 'id' primary key field.
    auto_now_add=True means created_at is set once, when the record is first saved.
    blank=True on ai_decision means it can be empty when the form is submitted —
    we fill it in the view before saving.
    """

    DECISION_CHOICES = [
        ('APPROVE', 'Approve'),
        ('EXCHANGE', 'Exchange'),
        ('ESCALATE', 'Escalate'),
        ('PENDING', 'Pending'),
    ]

    order_id = models.CharField(max_length=100)
    product_name = models.CharField(max_length=255)
    reason = models.TextField()

    # These are filled by the AI, not the user
    ai_decision = models.CharField(
        max_length=20,
        choices=DECISION_CHOICES,
        default='PENDING',
        blank=True
    )
    ai_explanation = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # Newest first

    def __str__(self):
        return f"[{self.ai_decision}] {self.order_id} - {self.product_name}"
