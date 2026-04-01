from django.contrib import admin
from .models import ReturnRequest


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    """
    Registers ReturnRequest in the Django admin panel.
    Visit http://localhost:8000/admin/ after creating a superuser.
    list_display controls which columns appear in the list view.
    list_filter adds a sidebar filter by decision type.
    """
    list_display = ['order_id', 'product_name', 'ai_decision', 'created_at']
    list_filter = ['ai_decision']
    search_fields = ['order_id', 'product_name']
    readonly_fields = ['ai_decision', 'ai_explanation', 'created_at']
