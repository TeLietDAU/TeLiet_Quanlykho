"""
apps/inventory/api_views.py
===========================
Class-Based Views exposing REST API for Inventory.
Delegates purely to Services avoiding DB coupling here.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError

from .serializers import (
    InventoryCheckCreateSerializer,
    LossRecordCreateSerializer,
    ReportFilterSerializer
)
from .services import InventoryService, LossService, ReportService
from .permissions import IsKhoOrAdmin, IsKeToanOrAdmin

class CreateInventoryCheckView(APIView):
    """
    API for creating a new Inventory Audit.
    Allowed Roles: KHO, ADMIN
    """
    permission_classes = [IsKhoOrAdmin]

    def post(self, request):
        serializer = InventoryCheckCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            val_data = serializer.validated_data
            audit = InventoryService.create_check(
                audit_date=val_data['audit_date'],
                note=val_data['note'],
                product_ids=val_data['product_ids'],
                user=request.user
            )
            return Response(
                {
                    'message': 'Đã khởi tạo phiên kiểm kê thành công.',
                    'audit_id': str(audit.id),
                    'audit_code': audit.audit_code
                },
                status=status.HTTP_201_CREATED
            )
        except DjangoValidationError as e:
            # Catch service-layer validation errors
            return Response({'error': str(e.message)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Lỗi server nội bộ', 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateLossRecordView(APIView):
    """
    API for manually logging inventory loss (e.g. Broken components).
    Allowed Roles: KHO, ADMIN
    """
    permission_classes = [IsKhoOrAdmin]

    def post(self, request):
        serializer = LossRecordCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            val_data = serializer.validated_data
            loss = LossService.create_loss(
                product_id=val_data['product_id'],
                loss_quantity=val_data['loss_quantity'],
                loss_type=val_data['loss_type'],
                loss_reason=val_data['loss_reason'],
                loss_date=val_data['loss_date'],
                user=request.user,
                audit_item_id=val_data.get('audit_item_id')
            )
            return Response(
                {
                    'message': 'Ghi nhận hao hụt thành công.',
                    'loss_code': loss.loss_code,
                    'loss_id': str(loss.id)
                },
                status=status.HTTP_201_CREATED
            )
        except DjangoValidationError as e:
            return Response({'error': str(e.message)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Lỗi nội bộ khi lưu hao hụt', 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LossReportView(APIView):
    """
    API for generating the comprehensive loss report with calculated percentages.
    Allowed Roles: KE_TOAN, ADMIN
    """
    permission_classes = [IsKeToanOrAdmin]

    def get(self, request):
        serializer = ReportFilterSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            val_data = serializer.validated_data
            report_data = ReportService.generate_loss_report(
                date_from=val_data.get('date_from'),
                date_to=val_data.get('date_to')
            )
            return Response({
                'message': 'Đã tải báo cáo thống kê hao hụt.',
                'data': report_data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Không thể tổng hợp báo cáo', 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
