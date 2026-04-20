"""
REST API views for inventory audit, loss workflows, and discrepancy reporting.
"""

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import InventoryAudit, InventoryLoss
from .permissions import (
    IsAdminRole,
    IsKhoOrAdmin,
    IsKeToanOrAdmin,
    IsKhoOrKeToanOrAdmin,
)
from .serializers import (
    InventoryAuditFilterSerializer,
    InventoryCheckCreateSerializer,
    InventoryAuditItemUpdateSerializer,
    LossFilterSerializer,
    LossRecordCreateSerializer,
    LossRecordUpdateSerializer,
    LossRejectSerializer,
)
from .services import InventoryService, LossService


def _display_user(user):
    if user is None:
        return ''
    if hasattr(user, 'full_name') and user.full_name:
        return user.full_name
    return getattr(user, 'username', '') or ''


def _serialize_audit_item(item):
    discrepancy = item.discrepancy
    return {
        'id': str(item.id),
        'product_id': str(item.product_id),
        'product_name': item.product.name,
        'system_quantity': item.system_quantity,
        'actual_quantity': item.actual_quantity,
        'discrepancy': discrepancy,
        'has_loss': discrepancy < 0,
        'note': item.note,
    }


def _serialize_audit(audit, include_items=False):
    data = {
        'id': str(audit.id),
        'audit_code': audit.audit_code,
        'audit_date': audit.audit_date,
        'status': audit.status,
        'status_label': audit.get_status_display(),
        'note': audit.note,
        'created_by': _display_user(audit.created_by),
        'approved_by': _display_user(audit.approved_by),
        'approved_at': audit.approved_at,
        'created_at': audit.created_at,
    }
    if include_items:
        data['items'] = [_serialize_audit_item(item) for item in audit.items.select_related('product').all()]
    return data


def _serialize_loss(loss):
    return {
        'id': str(loss.id),
        'loss_code': loss.loss_code,
        'product_id': str(loss.product_id),
        'product_name': loss.product.name,
        'loss_quantity': loss.loss_quantity,
        'loss_type': loss.loss_type,
        'loss_type_label': loss.get_loss_type_display(),
        'loss_reason': loss.loss_reason,
        'loss_date': loss.loss_date,
        'unit_cost': loss.unit_cost,
        'total_loss_value': loss.total_loss_value,
        'status': loss.status,
        'status_label': loss.get_status_display(),
        'audit_id': str(loss.audit_item.audit_id) if loss.audit_item else None,
        'audit_item_id': str(loss.audit_item_id) if loss.audit_item_id else None,
        'created_by': _display_user(loss.created_by),
        'reviewed_by': _display_user(loss.reviewed_by),
        'reviewed_at': loss.reviewed_at,
        'rejection_note': loss.rejection_note,
        'created_at': loss.created_at,
    }


class InventoryAuditListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            permission_classes = [IsKhoOrAdmin]
        else:
            permission_classes = [IsKhoOrKeToanOrAdmin]
        return [permission() for permission in permission_classes]

    def get(self, request):
        serializer = InventoryAuditFilterSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        audits = InventoryService.list_checks(**serializer.validated_data)
        payload = [_serialize_audit(audit, include_items=False) for audit in audits]
        return Response({'count': len(payload), 'results': payload}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = InventoryCheckCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validated = serializer.validated_data
            audit = InventoryService.create_check(
                audit_date=validated['audit_date'],
                note=validated.get('note', ''),
                product_ids=validated['product_ids'],
                user=request.user,
            )
            return Response(
                {
                    'message': 'Da khoi tao phien kiem ke thanh cong.',
                    'audit_id': str(audit.id),
                    'audit_code': audit.audit_code,
                },
                status=status.HTTP_201_CREATED,
            )
        except DjangoValidationError as exc:
            return Response({'error': str(exc.message)}, status=status.HTTP_400_BAD_REQUEST)


class InventoryAuditDetailView(APIView):
    permission_classes = [IsKhoOrKeToanOrAdmin]

    def get(self, request, audit_id):
        try:
            audit, items, summary = InventoryService.get_check_detail(audit_id)
        except DjangoValidationError as exc:
            return Response({'error': str(exc.message)}, status=status.HTTP_404_NOT_FOUND)

        data = _serialize_audit(audit, include_items=False)
        data['items'] = [_serialize_audit_item(item) for item in items]
        data['summary'] = summary
        return Response(data, status=status.HTTP_200_OK)


class InventoryAuditItemUpdateView(APIView):
    permission_classes = [IsKhoOrAdmin]

    def patch(self, request, audit_id, item_id):
        serializer = InventoryAuditItemUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated = serializer.validated_data
        try:
            item = InventoryService.update_item_actual(
                check_id=audit_id,
                item_id=item_id,
                actual_quantity=validated['actual_quantity'],
                note=validated.get('note', ''),
            )
        except DjangoValidationError as exc:
            return Response({'error': str(exc.message)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                'message': 'Cap nhat so luong thuc te thanh cong.',
                'item': _serialize_audit_item(item),
            },
            status=status.HTTP_200_OK,
        )


class InventoryAuditSubmitView(APIView):
    permission_classes = [IsKhoOrAdmin]

    def post(self, request, audit_id):
        try:
            audit = InventoryService.submit_check(audit_id)
        except DjangoValidationError as exc:
            return Response({'error': str(exc.message)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                'message': 'Da nop phien kiem ke cho ke toan duyet.',
                'audit_id': str(audit.id),
                'status': audit.status,
            },
            status=status.HTTP_200_OK,
        )


class InventoryAuditApproveView(APIView):
    permission_classes = [IsKeToanOrAdmin]

    def post(self, request, audit_id):
        try:
            audit = InventoryService.approve_check(audit_id, request.user)
        except DjangoValidationError as exc:
            return Response({'error': str(exc.message)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                'message': 'Da duyet phien kiem ke. Ton kho da duoc cap nhat.',
                'audit_id': str(audit.id),
                'status': audit.status,
            },
            status=status.HTTP_200_OK,
        )


class InventoryAuditCancelView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request, audit_id):
        reason = request.data.get('reason', '')
        try:
            audit = InventoryService.cancel_check(audit_id, reason=reason)
        except DjangoValidationError as exc:
            return Response({'error': str(exc.message)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                'message': 'Da huy phien kiem ke.',
                'audit_id': str(audit.id),
                'status': audit.status,
            },
            status=status.HTTP_200_OK,
        )


class InventoryLossListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            permission_classes = [IsKhoOrAdmin]
        else:
            permission_classes = [IsKhoOrKeToanOrAdmin]
        return [permission() for permission in permission_classes]

    def get(self, request):
        serializer = LossFilterSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        losses = LossService.list_losses(**serializer.validated_data)
        payload = [_serialize_loss(loss) for loss in losses]
        return Response({'count': len(payload), 'results': payload}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = LossRecordCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated = serializer.validated_data
        try:
            loss = LossService.create_loss(
                product_id=validated['product_id'],
                loss_quantity=validated['loss_quantity'],
                loss_type=validated['loss_type'],
                loss_reason=validated['loss_reason'],
                loss_date=validated['loss_date'],
                unit_cost=validated.get('unit_cost'),
                user=request.user,
                audit_item_id=validated.get('audit_item_id'),
            )
        except DjangoValidationError as exc:
            return Response({'error': str(exc.message)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                'message': 'Ghi nhan hao hut thanh cong.',
                'loss_id': str(loss.id),
                'loss_code': loss.loss_code,
            },
            status=status.HTTP_201_CREATED,
        )


class InventoryLossDetailUpdateView(APIView):
    def get_permissions(self):
        if self.request.method == 'PATCH':
            permission_classes = [IsKhoOrAdmin]
        else:
            permission_classes = [IsKhoOrKeToanOrAdmin]
        return [permission() for permission in permission_classes]

    def get(self, request, loss_id):
        try:
            loss = LossService.get_loss(loss_id)
        except DjangoValidationError as exc:
            return Response({'error': str(exc.message)}, status=status.HTTP_404_NOT_FOUND)

        return Response(_serialize_loss(loss), status=status.HTTP_200_OK)

    def patch(self, request, loss_id):
        serializer = LossRecordUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            loss = LossService.update_loss(
                loss_id=loss_id,
                loss_type=serializer.validated_data.get('loss_type'),
                loss_reason=serializer.validated_data.get('loss_reason'),
            )
        except DjangoValidationError as exc:
            return Response({'error': str(exc.message)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                'message': 'Cap nhat phieu hao hut thanh cong.',
                'data': _serialize_loss(loss),
            },
            status=status.HTTP_200_OK,
        )


class InventoryLossApproveView(APIView):
    permission_classes = [IsKeToanOrAdmin]

    def post(self, request, loss_id):
        try:
            loss = LossService.approve_loss(loss_id, request.user)
        except DjangoValidationError as exc:
            return Response({'error': str(exc.message)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                'message': 'Da duyet phieu hao hut va cap nhat ton kho.',
                'loss_id': str(loss.id),
                'status': loss.status,
            },
            status=status.HTTP_200_OK,
        )


class InventoryLossRejectView(APIView):
    permission_classes = [IsKeToanOrAdmin]

    def post(self, request, loss_id):
        serializer = LossRejectSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            loss = LossService.reject_loss(
                loss_id=loss_id,
                reviewed_by=request.user,
                rejection_note=serializer.validated_data['rejection_note'],
            )
        except DjangoValidationError as exc:
            return Response({'error': str(exc.message)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                'message': 'Da tu choi phieu hao hut.',
                'loss_id': str(loss.id),
                'status': loss.status,
            },
            status=status.HTTP_200_OK,
        )


class InventoryLossStatsView(APIView):
    permission_classes = [IsKeToanOrAdmin]

    def get(self, request):
        filter_serializer = LossFilterSerializer(data=request.query_params)
        if not filter_serializer.is_valid():
            return Response({'errors': filter_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated = filter_serializer.validated_data
        data = LossService.get_stats(
            date_from=validated.get('date_from'),
            date_to=validated.get('date_to'),
            loss_type=validated.get('loss_type'),
            product_id=validated.get('product_id'),
        )
        return Response(data, status=status.HTTP_200_OK)


