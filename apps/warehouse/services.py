from .repositories import ImportReceiptRepository, ProductStockRepository, ExportReceiptRepository
from decimal import Decimal
from django.db import transaction

from apps.product.models import Category, Product

from .models import ImportReceiptItem, ExportReceiptItem, ProductStock


class ImportReceiptService:
    def __init__(self):
        self.repo = ImportReceiptRepository()

    def get_all(self):
        return ImportReceiptRepository.get_all()

    def get_by_id(self, receipt_id):
        return ImportReceiptRepository.get_by_id(receipt_id)

    def get_pending(self):
        return ImportReceiptRepository.get_by_status('PENDING')

    def get_by_user(self, user):
        return ImportReceiptRepository.get_by_user(user)

    def create_receipt(self, note, items_data, user):
        """
        Thủ kho tạo phiếu nhập.
        items_data: list of dict {product_id, quantity, unit_price, note}
        """
        if not items_data:
            return None, 'Phiếu phải có ít nhất 1 sản phẩm.'

        for idx, item in enumerate(items_data):
            if not item.get('product_id'):
                return None, f'Dòng {idx+1}: chưa chọn sản phẩm.'
            try:
                qty = float(item.get('quantity', 0))
            except (ValueError, TypeError):
                return None, f'Dòng {idx+1}: số lượng không hợp lệ.'
            if qty <= 0:
                return None, f'Dòng {idx+1}: số lượng phải lớn hơn 0.'
            item['quantity'] = qty

        receipt_data = {'note': note}
        receipt = ImportReceiptRepository.create_with_items(receipt_data, items_data, user)
        return receipt, None

    def approve_receipt(self, receipt_id, reviewed_by):
        """Kế toán duyệt phiếu"""
        receipt = ImportReceiptRepository.get_by_id(receipt_id)
        if not receipt:
            return False, 'Không tìm thấy phiếu.'
        if receipt.status != 'PENDING':
            return False, 'Chỉ có thể duyệt phiếu đang chờ duyệt.'
        ImportReceiptRepository.approve(receipt, reviewed_by)
        return True, f'Phiếu {receipt.receipt_code} đã được duyệt. Tồn kho đã được cập nhật.'

    def reject_receipt(self, receipt_id, reviewed_by, rejection_note):
        """Kế toán từ chối phiếu"""
        receipt = ImportReceiptRepository.get_by_id(receipt_id)
        if not receipt:
            return False, 'Không tìm thấy phiếu.'
        if receipt.status != 'PENDING':
            return False, 'Chỉ có thể từ chối phiếu đang chờ duyệt.'
        if not rejection_note or not rejection_note.strip():
            return False, 'Vui lòng ghi lý do từ chối.'
        ImportReceiptRepository.reject(receipt, reviewed_by, rejection_note.strip())
        return True, f'Phiếu {receipt.receipt_code} đã bị từ chối.'

    def resubmit_receipt(self, receipt_id, note, items_data, user):
        """Thủ kho sửa lại phiếu bị từ chối và gửi lại"""
        receipt = ImportReceiptRepository.get_by_id(receipt_id)
        if not receipt:
            return None, 'Không tìm thấy phiếu.'
        if receipt.status != 'REJECTED':
            return None, 'Chỉ có thể gửi lại phiếu bị từ chối.'
        if receipt.created_by != user:
            return None, 'Bạn không có quyền sửa phiếu này.'

        if not items_data:
            return None, 'Phiếu phải có ít nhất 1 sản phẩm.'

        for idx, item in enumerate(items_data):
            try:
                qty = float(item.get('quantity', 0))
            except (ValueError, TypeError):
                return None, f'Dòng {idx+1}: số lượng không hợp lệ.'
            if qty <= 0:
                return None, f'Dòng {idx+1}: số lượng phải lớn hơn 0.'
            item['quantity'] = qty

        receipt = ImportReceiptRepository.resubmit(receipt, items_data, note)
        return receipt, None


class StockService:
    """Service xem tồn kho — dùng chung"""

    def get_all_stocks(self):
        return ProductStockRepository.get_all()

    def get_stock_info(self, product_id):
        return ProductStockRepository.get_stock(product_id)


class StockReportService:
    """Báo cáo tồn kho theo thời gian (US-23)."""

    @staticmethod
    def get_categories():
        return Category.objects.all().order_by('name')

    @staticmethod
    def _apply_export(balance, quantity):
        # Đồng bộ với logic kho hiện tại: không để âm tồn.
        updated = balance - quantity
        return updated if updated > 0 else Decimal('0')

    def build_report(self, from_date, to_date, category_id=None):
        products_qs = Product.objects.select_related('category').all().order_by('name')
        if category_id:
            products_qs = products_qs.filter(category_id=category_id)

        products = list(products_qs)
        if not products:
            zero = Decimal('0')
            return [], {
                'opening': zero,
                'import_qty': zero,
                'export_qty': zero,
                'closing': zero,
            }

        product_ids = [p.id for p in products]

        report_map = {}
        balances = {}
        for product in products:
            report_map[product.id] = {
                'product': product,
                'opening': Decimal('0'),
                'import_qty': Decimal('0'),
                'export_qty': Decimal('0'),
                'closing': Decimal('0'),
            }
            balances[product.id] = Decimal('0')

        import_items = ImportReceiptItem.objects.filter(
            product_id__in=product_ids,
            receipt__status='APPROVED',
            receipt__reviewed_at__date__lte=to_date,
        ).values('product_id', 'quantity', 'receipt__reviewed_at')

        export_items = ExportReceiptItem.objects.filter(
            product_id__in=product_ids,
            receipt__status='APPROVED',
            receipt__reviewed_at__date__lte=to_date,
        ).values('product_id', 'quantity', 'receipt__reviewed_at')

        pre_period_events = []
        in_period_events = []

        for row in import_items:
            event_date = row['receipt__reviewed_at'].date()
            event = (row['receipt__reviewed_at'], row['product_id'], Decimal(str(row['quantity'])), 'IMPORT')
            if event_date < from_date:
                pre_period_events.append(event)
            else:
                in_period_events.append(event)

        for row in export_items:
            event_date = row['receipt__reviewed_at'].date()
            event = (row['receipt__reviewed_at'], row['product_id'], Decimal(str(row['quantity'])), 'EXPORT')
            if event_date < from_date:
                pre_period_events.append(event)
            else:
                in_period_events.append(event)

        pre_period_events.sort(key=lambda x: (x[0], 0 if x[3] == 'IMPORT' else 1))
        in_period_events.sort(key=lambda x: (x[0], 0 if x[3] == 'IMPORT' else 1))

        # Tính tồn đầu kỳ bằng cách replay các giao dịch trước kỳ.
        for _, product_id, quantity, event_type in pre_period_events:
            if event_type == 'IMPORT':
                balances[product_id] += quantity
            else:
                balances[product_id] = self._apply_export(balances[product_id], quantity)

        for product_id, row in report_map.items():
            row['opening'] = balances[product_id]

        # Tính nhập/xuất trong kỳ và tồn cuối kỳ.
        for reviewed_at, product_id, quantity, event_type in in_period_events:
            event_date = reviewed_at.date()
            if event_date > to_date:
                continue

            if event_type == 'IMPORT':
                report_map[product_id]['import_qty'] += quantity
                balances[product_id] += quantity
            else:
                report_map[product_id]['export_qty'] += quantity
                balances[product_id] = self._apply_export(balances[product_id], quantity)

        for product_id, row in report_map.items():
            row['closing'] = balances[product_id]

        rows = [report_map[product.id] for product in products]

        totals = {
            'opening': sum((row['opening'] for row in rows), Decimal('0')),
            'import_qty': sum((row['import_qty'] for row in rows), Decimal('0')),
            'export_qty': sum((row['export_qty'] for row in rows), Decimal('0')),
            'closing': sum((row['closing'] for row in rows), Decimal('0')),
        }
        return rows, totals


class ExportReceiptService:
    def __init__(self):
        self.repo = ExportReceiptRepository()

    def get_all(self):
        return ExportReceiptRepository.get_all()

    def get_by_id(self, receipt_id):
        return ExportReceiptRepository.get_by_id(receipt_id)

    def get_pending(self):
        return ExportReceiptRepository.get_by_status('PENDING')

    def get_by_user(self, user):
        return ExportReceiptRepository.get_by_user(user)

    def create_receipt(self, note, items_data, user):
        """
        Thủ kho tạo phiếu xuất.
        items_data: list of dict {product_id, quantity, unit_price, note}
        """
        if not items_data:
            return None, 'Phiếu phải có ít nhất 1 sản phẩm.'

        for idx, item in enumerate(items_data):
            if not item.get('product_id'):
                return None, f'Dòng {idx+1}: chưa chọn sản phẩm.'
            try:
                qty = float(item.get('quantity', 0))
            except (ValueError, TypeError):
                return None, f'Dòng {idx+1}: số lượng không hợp lệ.'
            if qty <= 0:
                return None, f'Dòng {idx+1}: số lượng phải lớn hơn 0.'
            item['quantity'] = qty

        requested = {}
        for item in items_data:
            requested[item['product_id']] = requested.get(item['product_id'], 0) + item['quantity']

        with transaction.atomic():
            for product_id, requested_qty in requested.items():
                stock, _ = ProductStock.objects.select_for_update().get_or_create(
                    product_id=product_id,
                    defaults={'quantity': 0, 'reserved_quantity': 0}
                )
                if stock.available_quantity < requested_qty:
                    product_name = stock.product.name if stock.product else 'Sản phẩm'
                    return None, f'{product_name} chỉ còn khả dụng {stock.available_quantity}, yêu cầu {requested_qty}.'

            for product_id, requested_qty in requested.items():
                stock = ProductStock.objects.select_for_update().get(product_id=product_id)
                stock.reserved_quantity += requested_qty
                stock.save(update_fields=['reserved_quantity', 'last_updated'])

            receipt_data = {'note': note}
            receipt = ExportReceiptRepository.create_with_items(receipt_data, items_data, user)
            return receipt, None

    def approve_receipt(self, receipt_id, reviewed_by):
        """Kế toán duyệt phiếu"""
        receipt = ExportReceiptRepository.get_by_id(receipt_id)
        if not receipt:
            return False, 'Không tìm thấy phiếu.'
        if receipt.status != 'PENDING':
            return False, 'Chỉ có thể duyệt phiếu đang chờ duyệt.'
        ExportReceiptRepository.approve(receipt, reviewed_by)
        return True, f'Phiếu {receipt.receipt_code} đã được duyệt. Tồn kho đã được cập nhật.'

    def reject_receipt(self, receipt_id, reviewed_by, rejection_note):
        """Kế toán từ chối phiếu"""
        receipt = ExportReceiptRepository.get_by_id(receipt_id)
        if not receipt:
            return False, 'Không tìm thấy phiếu.'
        if receipt.status != 'PENDING':
            return False, 'Chỉ có thể từ chối phiếu đang chờ duyệt.'
        if not rejection_note or not rejection_note.strip():
            return False, 'Vui lòng ghi lý do từ chối.'
        ExportReceiptRepository.reject(receipt, reviewed_by, rejection_note.strip())
        return True, f'Phiếu {receipt.receipt_code} đã bị từ chối.'

    def resubmit_receipt(self, receipt_id, note, items_data, user):
        """Thủ kho sửa lại phiếu bị từ chối và gửi lại"""
        receipt = ExportReceiptRepository.get_by_id(receipt_id)
        if not receipt:
            return None, 'Không tìm thấy phiếu.'
        if receipt.status != 'REJECTED':
            return None, 'Chỉ có thể gửi lại phiếu bị từ chối.'
        if receipt.created_by != user:
            return None, 'Bạn không có quyền sửa phiếu này.'

        if not items_data:
            return None, 'Phiếu phải có ít nhất 1 sản phẩm.'

        for idx, item in enumerate(items_data):
            try:
                qty = float(item.get('quantity', 0))
            except (ValueError, TypeError):
                return None, f'Dòng {idx+1}: số lượng không hợp lệ.'
            if qty <= 0:
                return None, f'Dòng {idx+1}: số lượng phải lớn hơn 0.'
            item['quantity'] = qty

        try:
            receipt = ExportReceiptRepository.resubmit(receipt, items_data, note)
        except ValueError as exc:
            return None, str(exc)
        return receipt, None