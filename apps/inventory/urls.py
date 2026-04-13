"""
apps/inventory/urls.py
======================
Configures REST API URL endpoints.
"""

from django.urls import path
from .api_views import CreateInventoryCheckView, CreateLossRecordView, LossReportView

app_name = 'inventory_api'

urlpatterns = [
    # Inventory Check Route
    path('audits/create/', CreateInventoryCheckView.as_view(), name='audit-create'),
    
    # Loss Record Route
    path('losses/create/', CreateLossRecordView.as_view(), name='loss-create'),
    
    # Reporting Route
    path('reports/losses/', LossReportView.as_view(), name='loss-report-generate'),
]
