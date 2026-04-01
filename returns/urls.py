from django.urls import path
from .views import ReturnRequestListView, ReturnRequestDetailView

urlpatterns = [
    # List all returns + create a new one
    path('returns/', ReturnRequestListView.as_view(), name='return-list'),

    # Fetch a single return by its ID
    path('returns/<int:pk>/', ReturnRequestDetailView.as_view(), name='return-detail'),
]
