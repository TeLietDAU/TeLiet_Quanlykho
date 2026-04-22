"""
Request serializers for inventory APIs.
"""

from decimal import Decimal

from rest_framework import serializers

from .models import InventoryAudit, InventoryLoss


class InventoryAuditFilterSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=InventoryAudit.Status.choices, required=False)
    search = serializers.CharField(required=False, allow_blank=True)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)

    def validate(self, attrs):
        date_from = attrs.get('date_from')
        date_to = attrs.get('date_to')
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError({'date_to': 'Ngay ket thuc khong duoc nho hon ngay bat dau.'})
        return attrs


class InventoryCheckCreateSerializer(serializers.Serializer):
    audit_date = serializers.DateField(required=True)
    note = serializers.CharField(required=False, allow_blank=True, default='')
    product_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
    )


class InventoryAuditItemUpdateSerializer(serializers.Serializer):
    actual_quantity = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=Decimal('0'))
    note = serializers.CharField(required=False, allow_blank=True, default='')


class LossFilterSerializer(serializers.Serializer):
    loss_type = serializers.ChoiceField(choices=InventoryLoss.LossType.choices, required=False)
    status = serializers.ChoiceField(choices=InventoryLoss.Status.choices, required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    product_id = serializers.UUIDField(required=False)
    search = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        date_from = attrs.get('date_from')
        date_to = attrs.get('date_to')
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError({'date_to': 'Ngay ket thuc khong duoc nho hon ngay bat dau.'})
        return attrs


class LossRecordCreateSerializer(serializers.Serializer):
    product_id = serializers.UUIDField(required=True)
    loss_quantity = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=Decimal('0.01'))
    loss_type = serializers.ChoiceField(choices=InventoryLoss.LossType.choices)
    loss_reason = serializers.CharField(min_length=5)
    loss_date = serializers.DateField(required=True)
    unit_cost = serializers.DecimalField(max_digits=19, decimal_places=4, min_value=Decimal('0'), required=False)
    audit_item_id = serializers.UUIDField(required=False, allow_null=True)


class LossRecordUpdateSerializer(serializers.Serializer):
    loss_type = serializers.ChoiceField(choices=InventoryLoss.LossType.choices, required=False)
    loss_reason = serializers.CharField(min_length=5, required=False)

    def validate(self, attrs):
        if 'loss_type' not in attrs and 'loss_reason' not in attrs:
            raise serializers.ValidationError('Can it nhat 1 truong de cap nhat.')
        return attrs


class LossRejectSerializer(serializers.Serializer):
    rejection_note = serializers.CharField(min_length=3)
