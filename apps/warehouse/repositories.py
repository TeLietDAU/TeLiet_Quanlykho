from django.db import transaction
from django.utils import timezone
from .models import ImportReceipt, ImportReceiptItem, ProductStock, ExportReceipt, ExportReceiptItem


# ============================================================
# Import Receipt Repository
# ============================================================
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
        """Tạo mã phiếu tự động: PN-YYYYMMDD-XXX"""
        date_str = timezone.now().strftime('%Y%m%d')
        count = ImportReceipt.objects.filter(
            receipt_code__startswith=f'PN-{date_str}'
        ).count() + 1
        return f'PN-{date_str}-{count:03d}'

    @staticmethod
    @transaction.atomic
    def create_with_items(receipt_data, items_data, user):
        """Tạo phiếu nhập + các dòng sản phẩm trong 1 transaction"""
        receipt_data['receipt_code'] = ImportReceiptRepository.generate_receipt_code()
        receipt_data['created_by'] = user
        receipt_data['status'] = 'PENDING'

        receipt = ImportReceipt.objects.create(**receipt_data)

        item_instances = [
            ImportReceiptItem(
                receipt=receipt,
                product_id=item['product_id'],
                quantity=item['quantity'],
                unit_price=item.get('unit_price', 0),
                note=item.get('note', ''),
            )
            for item in items_data
        ]
        ImportReceiptItem.objects.bulk_create(item_instances)

        return receipt

    @staticmethod
    @transaction.atomic
    def approve(receipt, reviewed_by):
        """Kế toán duyệt → cộng vào tồn kho"""
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
        """Kế toán từ chối + ghi ghi chú"""
        receipt.status = 'REJECTED'
        receipt.reviewed_by = reviewed_by
        receipt.reviewed_at = timezone.now()
        receipt.rejection_note = rejection_note
        receipt.save()
        return receipt

    @staticmethod
    @transaction.atomic
    def resubmit(receipt, items_data, note=''):
        """Thủ kho sửa lại phiếu bị từ chối và gửi lại"""
        receipt.status = 'PENDING'
        receipt.rejection_note = ''
        receipt.note = note
        receipt.reviewed_by = None
        receipt.reviewed_at = None
        receipt.save()

        receipt.items.all().delete()
        item_instances = [
            ImportReceiptItem(
                receipt=receipt,
                product_id=item['product_id'],
                quantity=item['quantity'],
                unit_price=item.get('unit_price', 0),
                note=item.get('note', ''),
            )
            for item in items_data
        ]
        ImportReceiptItem.objects.bulk_create(item_instances)
        return receipt


# ============================================================
# Product Stock Repository
# ============================================================
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


# ============================================================
# Export Receipt Repository
# ============================================================
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
        """Tạo mã phiếu tự động: EX-YYYYMMDD-XXX"""
        date_str = timezone.now().strftime('%Y%m%d')
        count = ExportReceipt.objects.filter(
            receipt_code__startswith=f'EX-{date_str}'
        ).count() + 1
        return f'EX-{date_str}-{count:03d}'

    @staticmethod
    @transaction.atomic
    def create_with_items(receipt_data, items_data, user):
        """Tạo phiếu xuất + các dòng sản phẩm trong 1 transaction"""
        receipt_data['receipt_code'] = ExportReceiptRepository.generate_receipt_code()
        receipt_data['created_by'] = user
        receipt_data['status'] = 'PENDING'

        receipt = ExportReceipt.objects.create(**receipt_data)

        item_instances = [
            ExportReceiptItem(
                receipt=receipt,
                product_id=item['product_id'],
                quantity=item['quantity'],
                unit_price=item.get('unit_price', 0),
                note=item.get('note', ''),
            )
            for item in items_data
        ]
        ExportReceiptItem.objects.bulk_create(item_instances)

        return receipt

    @staticmethod
    def _extract_order_code_from_note(note):
        """
        Trích xuất mã đơn hàng từ note.
        Hỗ trợ format: 'Xuất hàng cho đơn DH-YYYYMMDD-XXX — KH: ...'
        hoặc bất kỳ chuỗi nào chứa 'DH-YYYYMMDD-XXX'
        """
        if not note:
            return None
        import re
        # Match DH- theo sau là digits-digits (format mới: DH-20260405-001)
        match = re.search(r'(DH-\d{8}-\d+)', note)
        if match:
            return match.group(1)
        # Fallback: format cũ DH-YYYY-XXXX
        match = re.search(r'(DH-\d{4}-\d+)', note)
        return match.group(1) if match else None

    @staticmethod
    @transaction.atomic
    def approve(receipt, reviewed_by):
        """
        Kế toán duyệt phiếu xuất:
        1. Trừ tồn kho
        2. Tự động chuyển đơn hàng sang DONE
        """
        receipt.status = 'APPROVED'
        receipt.reviewed_by = reviewed_by
        receipt.reviewed_at = timezone.now()
        receipt.rejection_note = ''
        receipt.save()

        # Trừ tồn kho
        for item in receipt.items.select_related('product').all():
            stock, _ = ProductStock.objects.get_or_create(
                product=item.product,
                defaults={'quantity': 0, 'reserved_quantity': 0}
            )
            stock.quantity -= item.quantity
            released = item.quantity if stock.reserved_quantity >= item.quantity else stock.reserved_quantity
            stock.reserved_quantity -= released
            if stock.quantity < 0:
                stock.quantity = 0  # Không cho âm kho
            if stock.reserved_quantity < 0:
                stock.reserved_quantity = 0
            stock.save()

        # Tự động cập nhật đơn hàng → DONE
        order = receipt.sales_order
        if order is None:
            order_code = ExportReceiptRepository._extract_order_code_from_note(receipt.note)
            if order_code:
                from apps.order.models import SalesOrder
                order = SalesOrder.objects.filter(order_code=order_code).first()

        if order and order.status in ['WAITING', 'CONFIRMED']:
            order.status = 'DONE'
            order.save(update_fields=['status'])

        return receipt

    @staticmethod
    def reject(receipt, reviewed_by, rejection_note):
        """Kế toán từ chối phiếu xuất + cập nhật đơn hàng về CONFIRMED"""
        receipt.status = 'REJECTED'
        receipt.reviewed_by = reviewed_by
        receipt.reviewed_at = timezone.now()
        receipt.rejection_note = rejection_note
        receipt.save()

        # Nhả phần đã giữ chỗ khi phiếu bị từ chối.
        for item in receipt.items.select_related('product').all():
            stock, _ = ProductStock.objects.get_or_create(
                product=item.product,
                defaults={'quantity': 0, 'reserved_quantity': 0}
            )
            released = item.quantity if stock.reserved_quantity >= item.quantity else stock.reserved_quantity
            stock.reserved_quantity -= released
            if stock.reserved_quantity < 0:
                stock.reserved_quantity = 0
            stock.save()

        # Đơn hàng liên quan → trả về CONFIRMED để có thể tạo phiếu xuất mới
        order = receipt.sales_order
        if order is None:
            order_code = ExportReceiptRepository._extract_order_code_from_note(receipt.note)
            if order_code:
                from apps.order.models import SalesOrder
                order = SalesOrder.objects.filter(order_code=order_code).first()

        if order and order.status == 'WAITING':
            order.status = 'CONFIRMED'
            order.save(update_fields=['status'])

        return receipt

    @staticmethod
    @transaction.atomic
    def resubmit(receipt, items_data, note=''):
        """Thủ kho sửa lại phiếu bị từ chối và gửi lại"""
        # Validate khả dụng trước khi giữ chỗ lại.
        requested_by_product = {}
        for item in items_data:
            product_id = item['product_id']
            requested_by_product[product_id] = requested_by_product.get(product_id, 0) + item['quantity']

        for product_id, requested_qty in requested_by_product.items():
            stock, _ = ProductStock.objects.select_for_update().get_or_create(
                product_id=product_id,
                defaults={'quantity': 0, 'reserved_quantity': 0}
            )
            if stock.available_quantity < requested_qty:
                from apps.product.models import Product
                product = Product.objects.filter(pk=product_id).first()
                product_name = product.name if product else 'Sản phẩm'
                raise ValueError(f'Không đủ tồn khả dụng để gửi lại phiếu cho {product_name}.')

        for product_id, requested_qty in requested_by_product.items():
            stock = ProductStock.objects.select_for_update().get(product_id=product_id)
            stock.reserved_quantity += requested_qty
            stock.save(update_fields=['reserved_quantity', 'last_updated'])

        receipt.status = 'PENDING'
        receipt.rejection_note = ''
        receipt.note = note
        receipt.reviewed_by = None
        receipt.reviewed_at = None
        receipt.save()

        receipt.items.all().delete()
        item_instances = [
            ExportReceiptItem(
                receipt=receipt,
                product_id=item['product_id'],
                quantity=item['quantity'],
                unit_price=item.get('unit_price', 0),
                note=item.get('note', ''),
            )
            for item in items_data
        ]
        ExportReceiptItem.objects.bulk_create(item_instances)

        # Đưa đơn hàng về WAITING để chờ duyệt lại
        order = receipt.sales_order
        if order is None:
            order_code = ExportReceiptRepository._extract_order_code_from_note(note)
            if order_code:
                from apps.order.models import SalesOrder
                order = SalesOrder.objects.filter(order_code=order_code).first()

        if order and order.status == 'CONFIRMED':
            order.status = 'WAITING'
            order.save(update_fields=['status'])

        return receipt