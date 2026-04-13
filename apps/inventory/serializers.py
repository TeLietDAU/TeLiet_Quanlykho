"""
apps/inventory/serializers.py
=============================
Serializers to validate inbound request data.
"""

from rest_framework import serializers
from .models import InventoryLoss


class InventoryCheckCreateSerializer(serializers.Serializer):
    """Validator for creating an inventory audit."""
    audit_date = serializers.DateField(
        required=True, 
        error_messages={'required': 'Ngày kiểm kê không được bỏ trống.'}
    )
    note = serializers.CharField(
        required=False, allow_blank=True, default=''
    )
    product_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
        error_messages={
            'empty': 'Phải cung cấp ít nhất 1 sản phẩm để kiểm kê.',
            'required': 'Danh sách định danh sản phẩm không được thiếu.'
        }
    )


class LossRecordCreateSerializer(serializers.Serializer):
    """Validator for manually creating a loss ticket."""
    product_id = serializers.UUIDField(required=True)
    loss_quantity = serializers.DecimalField(
        max_digits=15, decimal_places=2, min_value=0.01,
        error_messages={'min_value': 'Số lượng hao hụt phải luôn dương.'}
    )
    loss_type = serializers.ChoiceField(
        choices=InventoryLoss.LossType.choices,
        error_messages={'invalid_choice': 'Loại hao hụt không hợp lệ.'}
    )
    loss_reason = serializers.CharField(
        min_length=5, required=True,
        error_messages={'min_length': 'Lý do hao hụt quá ngắn (cần ít nhất 5 ký tự).'}
    )
    loss_date = serializers.DateField(required=True)
    audit_item_id = serializers.UUIDField(required=False, allow_null=True)


class ReportFilterSerializer(serializers.Serializer):
    """Validator for query parameters triggering reports."""
    date_from = serializers.DateField(required=False, allow_null=True)
    date_to = serializers.DateField(required=False, allow_null=True)

    def validate(self, data):
        """Cross-validate dates making sure logic sequence is sound."""
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError({
                'date_to': 'Ngày kết thúc không được nhỏ hơn ngày bắt đầu.'
            })
        return data
