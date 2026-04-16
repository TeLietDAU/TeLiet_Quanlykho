from django.db import transaction
from django.utils import timezone

from apps.order.models import SalesOrder

from .models import (
    ExportReceipt,
    ExportReceiptItem,
    ImportReceipt,
    ImportReceiptItem,
    ProductStock,
)
from .stock_utils import build_stock_payload


class ImportReceiptRepository:

    @staticmethod
    def get_all():
        return ImportReceipt.objects.select_related(
            'created_by', 'reviewed_by'
        ).prefetch_related('items__product').all()

    @staticmethod
    def get_by_id(receipt_id):
        try:
            return ImportReceipt.objects.select_related(
                'created_by', 'reviewed_by'
            ).prefetch_related('items__product').get(pk=receipt_id)
        except ImportReceipt.DoesNotExist:
            return None

    @staticmethod
    def get_by_status(status):
        return ImportReceipt.objects.select_related(
            'created_by', 'reviewed_by'
        ).prefetch_related('items__product').filter(status=status)

    @staticmethod
    def get_by_user(user):
        return ImportReceipt.objects.select_related(
            'created_by', 'reviewed_by'
        ).prefetch_related('items__product').filter(created_by=user)

    @staticmethod
    def generate_receipt_code():
        date_str = timezone.now().strftime('%Y%m%d')
        count = ImportReceipt.objects.filter(
            receipt_code__startswith=f'PN-{date_str}'
        ).count() + 1
        return f'PN-{date_str}-{count:03d}'

    @staticmethod
    @transaction.atomic
    def create_with_items(receipt_data, items_data, user):
        receipt_data['receipt_code'] = ImportReceiptRepository.generate_receipt_code()
        receipt_data['created_by'] = user
        receipt_data['status'] = 'PENDING'

        receipt = ImportReceipt.objects.create(**receipt_data)
        ImportReceiptItem.objects.bulk_create([
            ImportReceiptItem(
                receipt=receipt,
                product_id=item['product_id'],
                quantity=item['quantity'],
                unit_price=item.get('unit_price', 0),
                note=item.get('note', ''),
            )
            for item in items_data
        ])
        return receipt

    @staticmethod
    @transaction.atomic
    def approve(receipt, reviewed_by):
        receipt.status = 'APPROVED'
        receipt.reviewed_by = reviewed_by
        receipt.reviewed_at = timezone.now()
        receipt.rejection_note = ''
        receipt.save()

        for item in receipt.items.select_related('product').all():
            stock, _ = ProductStock.objects.get_or_create(
                product=item.product,
                defaults={'quantity': 0}
            )
            stock.quantity += item.quantity
            stock.save()

        return receipt

    @staticmethod
    def reject(receipt, reviewed_by, rejection_note):
        receipt.status = 'REJECTED'
        receipt.reviewed_by = reviewed_by
        receipt.reviewed_at = timezone.now()
        receipt.rejection_note = rejection_note
        receipt.save()
        return receipt

    @staticmethod
    @transaction.atomic
    def resubmit(receipt, items_data, note=''):
        receipt.status = 'PENDING'
        receipt.rejection_note = ''
        receipt.note = note
        receipt.reviewed_by = None
        receipt.reviewed_at = None
        receipt.save()

        receipt.items.all().delete()
        ImportReceiptItem.objects.bulk_create([
            ImportReceiptItem(
                receipt=receipt,
                product_id=item['product_id'],
                quantity=item['quantity'],
                unit_price=item.get('unit_price', 0),
                note=item.get('note', ''),
            )
            for item in items_data
        ])
        return receipt


class ProductStockRepository:

    @staticmethod
    def get_stock(product_id):
        try:
            return ProductStock.objects.select_related('product').get(product_id=product_id)
        except ProductStock.DoesNotExist:
            return None

    @staticmethod
    def get_all():
        return ProductStock.objects.select_related('product__category').all()

    @staticmethod
    def get_quantity(product_id):
        stock = ProductStockRepository.get_stock(product_id)
        return stock.quantity if stock else 0

    @staticmethod
    def get_stock_payload(product_id):
        return build_stock_payload(ProductStockRepository.get_quantity(product_id))


class ExportReceiptRepository:

    @staticmethod
    def get_all():
        return ExportReceipt.objects.select_related(
            'created_by', 'reviewed_by', 'sales_order'
        ).prefetch_related('items__product').all()

    @staticmethod
    def get_by_id(receipt_id):
        try:
            return ExportReceipt.objects.select_related(
                'created_by', 'reviewed_by', 'sales_order'
            ).prefetch_related('items__product').get(pk=receipt_id)
        except ExportReceipt.DoesNotExist:
            return None

    @staticmethod
    def get_by_status(status):
        return ExportReceipt.objects.select_related(
            'created_by', 'reviewed_by', 'sales_order'
        ).prefetch_related('items__product').filter(status=status)

    @staticmethod
    def get_by_user(user):
        return ExportReceipt.objects.select_related(
            'created_by', 'reviewed_by', 'sales_order'
        ).prefetch_related('items__product').filter(created_by=user)

    @staticmethod
    def generate_receipt_code():
        date_str = timezone.now().strftime('%Y%m%d')
        count = ExportReceipt.objects.filter(
            receipt_code__startswith=f'EX-{date_str}'
        ).count() + 1
        return f'EX-{date_str}-{count:03d}'

    @staticmethod
    @transaction.atomic
    def create_with_items(receipt_data, items_data, user):
        sales_order = receipt_data.get('sales_order')
        if sales_order:
            has_open_receipt = ExportReceipt.objects.filter(
                sales_order=sales_order,
                status__in=['PENDING', 'APPROVED'],
            ).exists()
            if has_open_receipt:
                raise ValueError(f'Đơn hàng {sales_order.order_code} đã có phiếu xuất đang xử lý hoặc đã duyệt.')

        receipt_data['receipt_code'] = ExportReceiptRepository.generate_receipt_code()
        receipt_data['created_by'] = user
        receipt_data['status'] = 'PENDING'

        receipt = ExportReceipt.objects.create(**receipt_data)
        ExportReceiptItem.objects.bulk_create([
            ExportReceiptItem(
                receipt=receipt,
                product_id=item['product_id'],
                quantity=item['quantity'],
                unit_price=item.get('unit_price', 0),
                note=item.get('note', ''),
            )
            for item in items_data
        ])

        if sales_order and sales_order.status == 'CONFIRMED':
            sales_order.status = 'WAITING'
            sales_order.save(update_fields=['status'])

        return receipt

    @staticmethod
    def _extract_order_code_from_note(note):
        if not note:
            return None
        import re
        match = re.search(r'(DH-\d{8}-\d+)', note)
        if match:
            return match.group(1)
        match = re.search(r'(DH-\d{4}-\d+)', note)
        return match.group(1) if match else None

    @staticmethod
    def _get_linked_order(receipt):
        if receipt.sales_order_id:
            return receipt.sales_order
        order_code = ExportReceiptRepository._extract_order_code_from_note(receipt.note)
        if not order_code:
            return None
        return SalesOrder.objects.filter(order_code=order_code).first()

    @staticmethod
    def _validate_stock_before_approve(receipt):
        insufficient_items = []
        for item in receipt.items.select_related('product').all():
            stock, _ = ProductStock.objects.get_or_create(
                product=item.product,
                defaults={'quantity': 0},
            )
            if stock.quantity < item.quantity:
                insufficient_items.append(
                    f'{item.product.name}: tồn {stock.quantity} {item.product.base_unit}, cần xuất {item.quantity} {item.product.base_unit}'
                )
        if insufficient_items:
            raise ValueError('Không thể duyệt phiếu xuất vì tồn kho không đủ: ' + '; '.join(insufficient_items))

    @staticmethod
    @transaction.atomic
    def approve(receipt, reviewed_by):
        ExportReceiptRepository._validate_stock_before_approve(receipt)

        receipt.status = 'APPROVED'
        receipt.reviewed_by = reviewed_by
        receipt.reviewed_at = timezone.now()
        receipt.rejection_note = ''
        receipt.save()

        for item in receipt.items.select_related('product').all():
            stock, _ = ProductStock.objects.get_or_create(
                product=item.product,
                defaults={'quantity': 0}
            )
            stock.quantity -= item.quantity
            if stock.quantity < 0:
                stock.quantity = 0
            stock.save()

        order = ExportReceiptRepository._get_linked_order(receipt)
        if order and order.status in ['WAITING', 'CONFIRMED']:
            order.status = 'DONE'
            order.save(update_fields=['status'])

        return receipt

    @staticmethod
    def reject(receipt, reviewed_by, rejection_note):
        receipt.status = 'REJECTED'
        receipt.reviewed_by = reviewed_by
        receipt.reviewed_at = timezone.now()
        receipt.rejection_note = rejection_note
        receipt.save()

        order = ExportReceiptRepository._get_linked_order(receipt)
        if order and order.status == 'WAITING':
            order.status = 'CONFIRMED'
            order.save(update_fields=['status'])

        return receipt

    @staticmethod
    @transaction.atomic
    def resubmit(receipt, items_data, note=''):
        receipt.status = 'PENDING'
        receipt.rejection_note = ''
        receipt.note = note
        receipt.reviewed_by = None
        receipt.reviewed_at = None
        receipt.save()

        receipt.items.all().delete()
        ExportReceiptItem.objects.bulk_create([
            ExportReceiptItem(
                receipt=receipt,
                product_id=item['product_id'],
                quantity=item['quantity'],
                unit_price=item.get('unit_price', 0),
                note=item.get('note', ''),
            )
            for item in items_data
        ])

        order = ExportReceiptRepository._get_linked_order(receipt)
        if order and order.status == 'CONFIRMED':
            order.status = 'WAITING'
            order.save(update_fields=['status'])

        return receipt
