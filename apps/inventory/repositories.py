"""
apps/inventory/repositories.py
================================
Pure data-access layer for the inventory module.
No business logic here, just ORM queries, optimizations, and DB transactions.
"""

from django.db import transaction
from django.db.models import F, Sum, Q, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone

from .models import InventoryAudit, InventoryAuditItem, InventoryLoss, ReportExportLog
from apps.warehouse.models import ProductStock


class InventoryRepository:
    """Repository for Inventory Checks (Audits)."""

    @staticmethod
    def get_by_id(check_id):
        """Retrieve a specific inventory check with its items."""
        try:
            return InventoryAudit.objects.select_related(
                'created_by', 'approved_by'
            ).prefetch_related(
                'items__product__category'
            ).get(id=check_id)
        except InventoryAudit.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def create_check(audit_date, note, product_ids, user):
        """
        Create a new inventory check and snapshot current system stock.
        Uses select_for_update to avoid race conditions during snapshotting.
        """
        date_str = timezone.now().strftime('%Y%m%d')
        count = InventoryAudit.objects.filter(audit_code__startswith=f'KK-{date_str}').count() + 1
        audit_code = f'KK-{date_str}-{count:03d}'

        audit = InventoryAudit.objects.create(
            audit_code=audit_code,
            audit_date=audit_date,
            note=note or '',
            status=InventoryAudit.Status.DRAFT,
            created_by=user,
        )

        # Lock stock rows during snapshot
        stocks = ProductStock.objects.select_for_update().filter(
            product_id__in=product_ids
        ).select_related('product')

        stock_map = {str(s.product_id): s.quantity for s in stocks}

        items = []
        for pid in product_ids:
            qty = stock_map.get(str(pid), 0)
            items.append(InventoryAuditItem(
                audit=audit,
                product_id=pid,
                system_quantity=qty,
                actual_quantity=qty,
            ))

        InventoryAuditItem.objects.bulk_create(items, ignore_conflicts=True)
        return audit

    @staticmethod
    def get_discrepancy(check_id):
        """
        Calculate discrepancy for a specific check directly via DB.
        Useful for reporting without loading all Python objects.
        """
        return InventoryAuditItem.objects.filter(audit_id=check_id).annotate(
            calculated_discrepancy=F('actual_quantity') - F('system_quantity')
        ).values(
            'product_id', 
            'product__name', 
            'system_quantity', 
            'actual_quantity', 
            'calculated_discrepancy'
        )

    @staticmethod
    @transaction.atomic
    def approve_check(audit, approved_by):
        """Mark check as approved and update system stock."""
        audit.status = InventoryAudit.Status.APPROVED
        audit.approved_by = approved_by
        audit.approved_at = timezone.now()
        audit.save(update_fields=['status', 'approved_by', 'approved_at', 'updated_at'])

        items = audit.items.select_related('product').all()
        for item in items:
            stock, _ = ProductStock.objects.select_for_update().get_or_create(
                product=item.product,
                defaults={'quantity': 0},
            )
            stock.quantity = item.actual_quantity
            stock.save(update_fields=['quantity', 'last_updated'])
        return audit


class LossRepository:
    """Repository for Loss Records."""

    @staticmethod
    @transaction.atomic
    def create_loss(product_id, loss_quantity, loss_type, loss_reason, loss_date, unit_cost, user, audit_item=None):
        """Create a new loss record."""
        date_str = timezone.now().strftime('%Y%m%d')
        count = InventoryLoss.objects.filter(loss_code__startswith=f'HH-{date_str}').count() + 1
        loss_code = f'HH-{date_str}-{count:03d}'

        return InventoryLoss.objects.create(
            loss_code=loss_code,
            audit_item=audit_item,
            product_id=product_id,
            loss_quantity=loss_quantity,
            loss_type=loss_type,
            loss_reason=loss_reason,
            loss_date=loss_date,
            unit_cost=unit_cost,
            status=InventoryLoss.Status.PENDING,
            created_by=user,
        )

    @staticmethod
    def get_by_check_id(check_id):
        """Retrieve all loss records generated from a specific inventory check."""
        return InventoryLoss.objects.select_related(
            'product__category', 'created_by', 'reviewed_by'
        ).filter(audit_item__audit_id=check_id)

    @staticmethod
    @transaction.atomic
    def approve_loss(loss, reviewed_by):
        """Approve a loss record and reduce system stock."""
        loss.status = InventoryLoss.Status.APPROVED
        loss.reviewed_by = reviewed_by
        loss.reviewed_at = timezone.now()
        loss.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'updated_at'])

        ProductStock.objects.filter(product=loss.product).update(
            quantity=F('quantity') - loss.loss_quantity
        )
        ProductStock.objects.filter(product=loss.product, quantity__lt=0).update(quantity=0)
        return loss


class ReportRepository:
    """Repository for generating reports and statistics."""

    @staticmethod
    def get_report_summary(date_from=None, date_to=None):
        """Get high-level summary of inventory checks and losses."""
        audit_qs = InventoryAudit.objects.filter(status=InventoryAudit.Status.APPROVED)
        loss_qs = InventoryLoss.objects.filter(status=InventoryLoss.Status.APPROVED)

        if date_from:
            audit_qs = audit_qs.filter(audit_date__gte=date_from)
            loss_qs = loss_qs.filter(loss_date__gte=date_from)
        if date_to:
            audit_qs = audit_qs.filter(audit_date__lte=date_to)
            loss_qs = loss_qs.filter(loss_date__lte=date_to)

        total_audits = audit_qs.count()
        total_loss_value = loss_qs.aggregate(
            total=Coalesce(Sum(F('loss_quantity') * F('unit_cost'), output_field=DecimalField()), 0, output_field=DecimalField())
        )['total']

        return {
            'total_approved_audits': total_audits,
            'total_loss_value': total_loss_value
        }

    @staticmethod
    def aggregate_loss_by_type(date_from=None, date_to=None):
        """Aggregate losses grouped by loss type."""
        qs = InventoryLoss.objects.filter(status=InventoryLoss.Status.APPROVED)
        
        if date_from:
            qs = qs.filter(loss_date__gte=date_from)
        if date_to:
            qs = qs.filter(loss_date__lte=date_to)

        return qs.values('loss_type').annotate(
            total_quantity=Sum('loss_quantity'),
            total_value=Sum(F('loss_quantity') * F('unit_cost'), output_field=DecimalField()),
            count=Sum(F('id').count() if False else F('loss_quantity') * 0 + 1)
        ).order_by('-total_value')
