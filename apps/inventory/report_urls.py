"""Report export API routes."""

from django.urls import path

from .report_views import (
    StockSummaryExportView,
    ImportHistoryExportView,
    ExportHistoryExportView,
    LossReportExportView,
    DiscrepancyExportView,
    AuditReportExportView,
)

app_name = 'inventory_reports'

urlpatterns = [
    path('stock-summary/export/', StockSummaryExportView.as_view(), name='stock-summary-export'),
    path('import-history/export/', ImportHistoryExportView.as_view(), name='import-history-export'),
    path('export-history/export/', ExportHistoryExportView.as_view(), name='export-history-export'),
    path('loss-report/export/', LossReportExportView.as_view(), name='loss-report-export'),
    path('discrepancy/export/', DiscrepancyExportView.as_view(), name='discrepancy-export'),
    path('audit-report/export/', AuditReportExportView.as_view(), name='audit-report-export'),
]
