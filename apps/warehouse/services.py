from decimal import Decimal

from apps.product.models import Product

from .excel_utils import parse_receipt_excel
from .repositories import ImportReceiptRepository, ProductStockRepository, ExportReceiptRepository
from .stock_utils import build_stock_payload


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
        if not items_data:
            return None, 'Phiếu phải có ít nhất 1 sản phẩm.'

        cleaned_items, error = self._validate_items(items_data)
        if error:
            return None, error

        receipt_data = {'note': note}
        receipt = ImportReceiptRepository.create_with_items(receipt_data, cleaned_items, user)
        return receipt, None

    def import_receipts_from_excel(self, uploaded_file, user):
        groups = parse_receipt_excel(uploaded_file)
        created = []
        for group in groups:
            receipt, error = self.create_receipt(group.receipt_note, group.items, user)
            if error:
                raise ValueError(error)
            created.append(receipt)
        return created

    def approve_receipt(self, receipt_id, reviewed_by):
        if reviewed_by.role not in ('KE_TOAN', 'ADMIN') and not reviewed_by.is_superuser:
            return False, 'Bạn không có quyền duyệt phiếu.'
        receipt = ImportReceiptRepository.get_by_id(receipt_id)
        if not receipt:
            return False, 'Không tìm thấy phiếu.'
        if receipt.status != 'PENDING':
            return False, 'Chỉ có thể duyệt phiếu đang chờ duyệt.'
        ImportReceiptRepository.approve(receipt, reviewed_by)
        return True, f'Phiếu {receipt.receipt_code} đã được duyệt. Tồn kho đã được cập nhật.'

    def reject_receipt(self, receipt_id, reviewed_by, rejection_note):
        if reviewed_by.role not in ('KE_TOAN', 'ADMIN') and not reviewed_by.is_superuser:
            return False, 'Bạn không có quyền từ chối phiếu.'
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
        receipt = ImportReceiptRepository.get_by_id(receipt_id)
        if not receipt:
            return None, 'Không tìm thấy phiếu.'
        if receipt.status != 'REJECTED':
            return None, 'Chỉ có thể gửi lại phiếu bị từ chối.'
        if receipt.created_by != user:
            return None, 'Bạn không có quyền sửa phiếu này.'

        if not items_data:
            return None, 'Phiếu phải có ít nhất 1 sản phẩm.'

        cleaned_items, error = self._validate_items(items_data)
        if error:
            return None, error

        receipt = ImportReceiptRepository.resubmit(receipt, cleaned_items, note)
        return receipt, None

    def _validate_items(self, items_data):
        cleaned_items = []
        for idx, item in enumerate(items_data):
            if not item.get('product_id'):
                return None, f'Dòng {idx + 1}: chưa chọn sản phẩm.'
            try:
                qty = Decimal(str(item.get('quantity', 0)))
            except Exception:
                return None, f'Dòng {idx + 1}: số lượng không hợp lệ.'
            try:
                unit_price = Decimal(str(item.get('unit_price', 0)))
            except Exception:
                return None, f'Dòng {idx + 1}: đơn giá không hợp lệ.'
            if qty <= 0:
                return None, f'Dòng {idx + 1}: số lượng phải lớn hơn 0.'
            if unit_price < 0:
                return None, f'Dòng {idx + 1}: đơn giá phải lớn hơn hoặc bằng 0.'
            cleaned_items.append({
                'product_id': item['product_id'],
                'quantity': qty,
                'unit_price': unit_price,
                'note': item.get('note', ''),
            })
        return cleaned_items, None


class StockService:

    def get_all_stocks(self):
        products = Product.objects.select_related('category').all().order_by('name')
        stock_map = {
            str(stock.product_id): stock
            for stock in ProductStockRepository.get_all()
        }
        rows = []
        for product in products:
            stock = stock_map.get(str(product.id))
            payload = build_stock_payload(stock.quantity if stock else 0)
            rows.append({
                'product': product,
                'quantity': payload['stock_quantity'],
                'stock_status': payload['stock_status'],
                'stock_status_label': payload['stock_status_label'],
                'last_updated': stock.last_updated if stock else None,
            })
        return rows

    def get_stock_info(self, product_id):
        return ProductStockRepository.get_stock(product_id)

    def get_product_stock_payload(self, product_id):
        return ProductStockRepository.get_stock_payload(product_id)


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

    def create_receipt(self, note, items_data, user, sales_order=None):
        if not items_data:
            return None, 'Phiếu phải có ít nhất 1 sản phẩm.'

        cleaned_items, error = self._validate_items(items_data)
        if error:
            return None, error

        receipt_data = {'note': note, 'sales_order': sales_order}
        try:
            receipt = ExportReceiptRepository.create_with_items(receipt_data, cleaned_items, user)
        except ValueError as exc:
            return None, str(exc)
        return receipt, None

    def import_receipts_from_excel(self, uploaded_file, user):
        groups = parse_receipt_excel(uploaded_file)
        created = []
        for group in groups:
            receipt, error = self.create_receipt(
                group.receipt_note,
                group.items,
                user,
                sales_order=group.sales_order,
            )
            if error:
                raise ValueError(error)
            created.append(receipt)
        return created

    def approve_receipt(self, receipt_id, reviewed_by):
        if reviewed_by.role not in ('KE_TOAN', 'ADMIN') and not reviewed_by.is_superuser:
            return False, 'Bạn không có quyền duyệt phiếu.'
        receipt = ExportReceiptRepository.get_by_id(receipt_id)
        if not receipt:
            return False, 'Không tìm thấy phiếu.'
        if receipt.status != 'PENDING':
            return False, 'Chỉ có thể duyệt phiếu đang chờ duyệt.'
        try:
            ExportReceiptRepository.approve(receipt, reviewed_by)
        except ValueError as exc:
            return False, str(exc)
        return True, f'Phiếu {receipt.receipt_code} đã được duyệt. Tồn kho đã được cập nhật.'

    def reject_receipt(self, receipt_id, reviewed_by, rejection_note):
        if reviewed_by.role not in ('KE_TOAN', 'ADMIN') and not reviewed_by.is_superuser:
            return False, 'Bạn không có quyền từ chối phiếu.'
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
        receipt = ExportReceiptRepository.get_by_id(receipt_id)
        if not receipt:
            return None, 'Không tìm thấy phiếu.'
        if receipt.status != 'REJECTED':
            return None, 'Chỉ có thể gửi lại phiếu bị từ chối.'
        if receipt.created_by != user:
            return None, 'Bạn không có quyền sửa phiếu này.'

        if not items_data:
            return None, 'Phiếu phải có ít nhất 1 sản phẩm.'

        cleaned_items, error = self._validate_items(items_data)
        if error:
            return None, error

        receipt = ExportReceiptRepository.resubmit(receipt, cleaned_items, note)
        return receipt, None

    def _validate_items(self, items_data):
        cleaned_items = []
        for idx, item in enumerate(items_data):
            if not item.get('product_id'):
                return None, f'Dòng {idx + 1}: chưa chọn sản phẩm.'
            try:
                qty = Decimal(str(item.get('quantity', 0)))
            except Exception:
                return None, f'Dòng {idx + 1}: số lượng không hợp lệ.'
            try:
                unit_price = Decimal(str(item.get('unit_price', 0)))
            except Exception:
                return None, f'Dòng {idx + 1}: đơn giá không hợp lệ.'
            if qty <= 0:
                return None, f'Dòng {idx + 1}: số lượng phải lớn hơn 0.'
            if unit_price < 0:
                return None, f'Dòng {idx + 1}: đơn giá phải lớn hơn hoặc bằng 0.'
            cleaned_items.append({
                'product_id': item['product_id'],
                'quantity': qty,
                'unit_price': unit_price,
                'note': item.get('note', ''),
            })
        return cleaned_items, None

