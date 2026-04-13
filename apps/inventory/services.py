"""
apps/inventory/services.py
==========================
Business Logic Layer for Inventory, Loss, and Reporting.

Rules:
- Validates inputs 
- Handles business state checks
- Exclusively uses the corresponding Repositories for data queries
- Raises meaningful Python exceptions
"""

from decimal import Decimal
from django.core.exceptions import ValidationError

from .repositories import InventoryRepository, LossRepository, ReportRepository
from .models import InventoryAudit, InventoryLoss
from apps.warehouse.models import Product


class InventoryService:
    """Service handling business rules for Inventory Audits (Checks)."""

    @staticmethod
    def create_check(audit_date, note, product_ids, user):
        """
        Validate inputs and orchestrate inventory check creation.
        """
        if not product_ids:
            raise ValidationError("Cần ít nhất 1 sản phẩm để thực hiện kiểm kê.")
            
        validated_products = list(Product.objects.filter(id__in=product_ids).values_list('id', flat=True))
        if len(validated_products) != len(product_ids):
            raise ValidationError("Có sản phẩm không hợp lệ hoặc đã bị xóa.")

        return InventoryRepository.create_check(
            audit_date=audit_date,
            note=note,
            product_ids=validated_products,
            user=user
        )

    @staticmethod
    def approve_check(check_id, approved_by):
        """Validate check state and approve it."""
        audit = InventoryRepository.get_by_id(check_id)
        if not audit:
            raise ValidationError("Không tìm thấy phiên kiểm kê.")
            
        if audit.status != InventoryAudit.Status.SUBMITTED:
            raise ValidationError(f"Không thể duyệt phiên ở trạng thái {audit.status}.")

        return InventoryRepository.approve_check(audit, approved_by)

    @staticmethod
    def get_check_discrepancy(check_id):
        """Retrieve actual vs system discrepancies via Repository."""
        audit = InventoryRepository.get_by_id(check_id)
        if not audit:
            raise ValidationError("Không tìm thấy phiên kiểm kê.")

        discrepancies = InventoryRepository.get_discrepancy(check_id)
        
        # Enrich with additional business aggregations if needed
        result = []
        for d in discrepancies:
            item_discrepancy = d['calculated_discrepancy']
            d['status_flag'] = 'SHORTAGE' if item_discrepancy < 0 else 'SURPLUS' if item_discrepancy > 0 else 'MATCH'
            result.append(d)
                
        return result


class LossService:
    """Service handling business rules for Loss Tracking."""

    @staticmethod
    def create_loss(product_id, loss_quantity, loss_type, loss_reason, loss_date, user, audit_item_id=None):
        """
        Validate and create loss records.
        Applies strict classification validation.
        """
        if float(loss_quantity) <= 0:
            raise ValidationError("Số lượng hao hụt phải luôn dương (>0).")
            
        valid_types = [choice[0] for choice in InventoryLoss.LossType.choices]
        if loss_type not in valid_types:
            raise ValidationError(f"Loại hao hụt không hợp lệ. Hỗ trợ: {', '.join(valid_types)}.")
            
        if not loss_reason or len(loss_reason.strip()) < 5:
            raise ValidationError("Vui lòng ghi chú lý do / hoàn cảnh hao hụt rõ ràng.")

        product = Product.objects.filter(id=product_id).first()
        if not product:
            raise ValidationError("Không tìm thấy sản phẩm.")

        # Optionally validate audit_item linkage
        audit_item = None
        if audit_item_id:
            from .models import InventoryAuditItem
            audit_item = InventoryAuditItem.objects.filter(id=audit_item_id).first()
            if not audit_item:
                raise ValidationError("Liên kết dòng kiểm kê không hợp lệ.")

        return LossRepository.create_loss(
            product_id=product_id,
            loss_quantity=loss_quantity,
            loss_type=loss_type,
            loss_reason=loss_reason,
            loss_date=loss_date,
            unit_cost=product.base_price,
            user=user,
            audit_item=audit_item
        )


class ReportService:
    """Service handling business metrics, percentages and reports."""

    @staticmethod
    def generate_loss_report(date_from=None, date_to=None):
        """
        Generates grouped statistics on losses, calculating percentages
        against the overall lost value in the given date range.
        """
        summary = ReportRepository.get_report_summary(date_from=date_from, date_to=date_to)
        aggregations = list(ReportRepository.aggregate_loss_by_type(date_from=date_from, date_to=date_to))

        total_value = summary['total_loss_value'] or Decimal('0.00')

        # Add metric percentage calculation locally based on retrieved values
        for agg in aggregations:
            agg_val = agg['total_value'] or Decimal('0.00')
            if total_value > 0:
                agg['percentage_of_total_cost'] = round((agg_val / total_value) * 100, 2)
            else:
                agg['percentage_of_total_cost'] = Decimal('0.00')
            
            # Formulate human readable type name
            type_label = dict(InventoryLoss.LossType.choices).get(agg['loss_type'], 'Khác')
            agg['type_label'] = type_label

        return {
            'overall_summary': {
                'total_audits_passed': summary['total_approved_audits'],
                'total_impact_value': total_value
            },
            'breakdown_by_type': aggregations
        }
