"""Export endpoints for inventory reports."""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsKeToanOrAdmin
from .repositories import ReportRepository
from .serializers import ExportRequestSerializer
from .reports import (
    StockSummaryReportGenerator,
    ImportHistoryReportGenerator,
    ExportHistoryReportGenerator,
    LossReportGenerator,
    DiscrepancyReportGenerator,
    AuditReportGenerator,
)


def _export_filters(validated):
    filters = {}
    for key in ('date_from', 'date_to', 'loss_type', 'category_id', 'audit_id'):
        value = validated.get(key)
        if value not in (None, ''):
            filters[key] = str(value)
    return filters


class StockSummaryExportView(APIView):
    permission_classes = [IsKeToanOrAdmin]

    def get(self, request):
        serializer = ExportRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated = serializer.validated_data
        fmt = validated.get('format', 'excel')
        rows = list(ReportRepository.stock_summary_rows(category_id=validated.get('category_id')))

        generator = StockSummaryReportGenerator(rows, filters=_export_filters(validated))
        response = generator.as_http_response(fmt)

        ReportRepository.log_export(
            report_type='STOCK_SUMMARY',
            export_format=fmt.upper(),
            exported_by=request.user,
            filter_params=_export_filters(validated),
            row_count=len(rows),
        )
        return response


class ImportHistoryExportView(APIView):
    permission_classes = [IsKeToanOrAdmin]

    def get(self, request):
        serializer = ExportRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated = serializer.validated_data
        fmt = validated.get('format', 'excel')
        rows = list(
            ReportRepository.import_history_rows(
                date_from=validated.get('date_from'),
                date_to=validated.get('date_to'),
            )
        )

        generator = ImportHistoryReportGenerator(rows, filters=_export_filters(validated))
        response = generator.as_http_response(fmt)

        ReportRepository.log_export(
            report_type='IMPORT_HISTORY',
            export_format=fmt.upper(),
            exported_by=request.user,
            filter_params=_export_filters(validated),
            row_count=len(rows),
        )
        return response


class ExportHistoryExportView(APIView):
    permission_classes = [IsKeToanOrAdmin]

    def get(self, request):
        serializer = ExportRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated = serializer.validated_data
        fmt = validated.get('format', 'excel')
        rows = list(
            ReportRepository.export_history_rows(
                date_from=validated.get('date_from'),
                date_to=validated.get('date_to'),
            )
        )

        generator = ExportHistoryReportGenerator(rows, filters=_export_filters(validated))
        response = generator.as_http_response(fmt)

        ReportRepository.log_export(
            report_type='EXPORT_HISTORY',
            export_format=fmt.upper(),
            exported_by=request.user,
            filter_params=_export_filters(validated),
            row_count=len(rows),
        )
        return response


class LossReportExportView(APIView):
    permission_classes = [IsKeToanOrAdmin]

    def get(self, request):
        serializer = ExportRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated = serializer.validated_data
        fmt = validated.get('format', 'excel')
        rows = list(
            ReportRepository.loss_report_rows(
                date_from=validated.get('date_from'),
                date_to=validated.get('date_to'),
                loss_type=validated.get('loss_type'),
            )
        )

        generator = LossReportGenerator(rows, filters=_export_filters(validated))
        response = generator.as_http_response(fmt)

        ReportRepository.log_export(
            report_type='LOSS_REPORT',
            export_format=fmt.upper(),
            exported_by=request.user,
            filter_params=_export_filters(validated),
            row_count=len(rows),
        )
        return response


class DiscrepancyExportView(APIView):
    permission_classes = [IsKeToanOrAdmin]

    def get(self, request):
        serializer = ExportRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated = serializer.validated_data
        fmt = validated.get('format', 'excel')
        rows = list(
            ReportRepository.discrepancy_rows(
                category_id=validated.get('category_id'),
            )
        )

        generator = DiscrepancyReportGenerator(rows, filters=_export_filters(validated))
        response = generator.as_http_response(fmt)

        ReportRepository.log_export(
            report_type='DISCREPANCY',
            export_format=fmt.upper(),
            exported_by=request.user,
            filter_params=_export_filters(validated),
            row_count=len(rows),
        )
        return response


class AuditReportExportView(APIView):
    permission_classes = [IsKeToanOrAdmin]

    def get(self, request):
        serializer = ExportRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated = serializer.validated_data
        audit_id = validated.get('audit_id')
        if not audit_id:
            return Response({'error': 'audit_id la bat buoc cho bao cao kiem ke.'}, status=status.HTTP_400_BAD_REQUEST)

        fmt = validated.get('format', 'excel')
        audit, rows = ReportRepository.audit_report_rows(audit_id)
        if audit is None:
            return Response({'error': 'Khong tim thay phien kiem ke.'}, status=status.HTTP_404_NOT_FOUND)

        generator = AuditReportGenerator(audit=audit, data=rows, filters=_export_filters(validated))
        response = generator.as_http_response(fmt)

        ReportRepository.log_export(
            report_type='AUDIT_REPORT',
            export_format=fmt.upper(),
            exported_by=request.user,
            filter_params=_export_filters(validated),
            row_count=len(rows),
        )
        return response
