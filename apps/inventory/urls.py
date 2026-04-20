"""Inventory API routes."""

from django.urls import path

from .api_views import (
    InventoryAuditListCreateView,
    InventoryAuditDetailView,
    InventoryAuditItemUpdateView,
    InventoryAuditSubmitView,
    InventoryAuditApproveView,
    InventoryAuditCancelView,
    InventoryLossListCreateView,
    InventoryLossDetailUpdateView,
    InventoryLossApproveView,
    InventoryLossRejectView,
    InventoryLossStatsView,
)

app_name = 'inventory_api'

urlpatterns = [
    # Audit workflow
    path('audits/', InventoryAuditListCreateView.as_view(), name='audit-list-create'),
    path('audits/<uuid:audit_id>/', InventoryAuditDetailView.as_view(), name='audit-detail'),
    path('audits/<uuid:audit_id>/items/<uuid:item_id>/', InventoryAuditItemUpdateView.as_view(), name='audit-item-update'),
    path('audits/<uuid:audit_id>/submit/', InventoryAuditSubmitView.as_view(), name='audit-submit'),
    path('audits/<uuid:audit_id>/approve/', InventoryAuditApproveView.as_view(), name='audit-approve'),
    path('audits/<uuid:audit_id>/cancel/', InventoryAuditCancelView.as_view(), name='audit-cancel'),

    # Loss workflow
    path('losses/', InventoryLossListCreateView.as_view(), name='loss-list-create'),
    path('losses/stats/', InventoryLossStatsView.as_view(), name='loss-stats'),
    path('losses/<uuid:loss_id>/', InventoryLossDetailUpdateView.as_view(), name='loss-detail-update'),
    path('losses/<uuid:loss_id>/approve/', InventoryLossApproveView.as_view(), name='loss-approve'),
    path('losses/<uuid:loss_id>/reject/', InventoryLossRejectView.as_view(), name='loss-reject'),
]
