from .repositories import SalesOrderRepository
from decimal import Decimal
from django.db import transaction

class SalesOrderService:

    # Luồng trạng thái HỢP LỆ — chỉ đi 1 chiều, không quay lại
    VALID_TRANSITIONS = {
        'CONFIRMED': ['WAITING', 'CANCELLED'],
        'WAITING':   ['DONE', 'CANCELLED'],
        'DONE':      [],
        'CANCELLED': [],
    }

    def __init__(self):
        self.repo = SalesOrderRepository()

    def get_all(self, status=None, search=None):
        return SalesOrderRepository.get_all(status=status, search=search)

    def get_by_id(self, order_id):
        return SalesOrderRepository.get_by_id(order_id)

    def get_by_user(self, user):
        return SalesOrderRepository.get_by_user(user)

    def create_order(self, customer_name, customer_phone, note, items_data, user):
        """
        Sale tạo đơn hàng.
        Hệ thống tự kiểm tra kho và trừ ngay nếu đủ.
        Trả về (order, None) hoặc (None, errors_list)
        """
        if not customer_name or not customer_name.strip():
            return None, [{'message': 'Vui lòng nhập tên khách hàng.'}]

        if not items_data:
            return None, [{'message': 'Đơn hàng phải có ít nhất 1 sản phẩm.'}]

        cleaned_items = []
        for idx, item in enumerate(items_data):
            if not item.get('product_id'):
                return None, [{'message': f'Dòng {idx+1}: chưa chọn sản phẩm.'}]
            try:
                qty = Decimal(str(item.get('quantity', 0)))
            except (ValueError, TypeError):
                return None, [{'message': f'Dòng {idx+1}: số lượng không hợp lệ.'}]
            if qty <= 0:
                return None, [{'message': f'Dòng {idx+1}: số lượng phải lớn hơn 0.'}]
            item['quantity'] = qty
            cleaned_items.append(item)

        order_data = {
            'customer_name': customer_name.strip(),
            'customer_phone': customer_phone.strip() if customer_phone else '',
            'note': note or '',
        }

        order, errors = SalesOrderRepository.create_with_items(order_data, cleaned_items, user)
        return order, errors

    def update_status(self, order_id, new_status, updated_by=None):
        order = SalesOrderRepository.get_by_id(order_id)
        if not order:
            return False, 'Không tìm thấy đơn hàng.'

        # Kiểm tra luồng hợp lệ
        allowed = self.VALID_TRANSITIONS.get(order.status, [])
        if new_status not in allowed:
            status_labels = {
                'CONFIRMED': 'Đã xác nhận',
                'WAITING': 'Chờ lấy hàng',
                'DONE': 'Hoàn thành',
                'CANCELLED': 'Đã hủy',
            }
            current_label = status_labels.get(order.status, order.status)
            new_label = status_labels.get(new_status, new_status)
            return False, f'Không thể chuyển từ "{current_label}" sang "{new_label}".'

        with transaction.atomic():
            # Đơn ở WAITING phải giữ chỗ tồn kho trước khi tạo phiếu xuất.
            if new_status == 'WAITING':
                can_reserve, reserve_message = self._reserve_stock_for_order(order)
                if not can_reserve:
                    return False, reserve_message

            SalesOrderRepository.update_status(order, new_status)

            if new_status == 'WAITING':
                if updated_by is None:
                    self._release_reserved_stock_for_order(order)
                    order.status = 'CONFIRMED'
                    order.save(update_fields=['status'])
                    return False, 'Thiếu người thực hiện để tạo phiếu xuất.'

                created, create_message = self._create_export_receipt_for_order(order, updated_by)
                if not created:
                    self._release_reserved_stock_for_order(order)
                    order.status = 'CONFIRMED'
                    order.save(update_fields=['status'])
                    return False, create_message

        return True, 'Cập nhật trạng thái thành công.'

    def _reserve_stock_for_order(self, order):
        from apps.warehouse.models import ProductStock

        items = list(order.items.select_related('product').all())
        shortage_messages = []

        for item in items:
            stock, _ = ProductStock.objects.select_for_update().get_or_create(
                product=item.product,
                defaults={'quantity': 0, 'reserved_quantity': 0}
            )
            if stock.available_quantity < item.quantity:
                shortage_messages.append(
                    f'"{item.product.name}" chỉ còn khả dụng {stock.available_quantity}, cần {item.quantity}.'
                )

        if shortage_messages:
            return False, ' ; '.join(shortage_messages)

        for item in items:
            stock = ProductStock.objects.select_for_update().get(product=item.product)
            stock.reserved_quantity += item.quantity
            stock.save(update_fields=['reserved_quantity', 'last_updated'])

        return True, None

    def _release_reserved_stock_for_order(self, order):
        from apps.warehouse.models import ProductStock

        for item in order.items.select_related('product').all():
            stock, _ = ProductStock.objects.select_for_update().get_or_create(
                product=item.product,
                defaults={'quantity': 0, 'reserved_quantity': 0}
            )
            released = item.quantity if stock.reserved_quantity >= item.quantity else stock.reserved_quantity
            stock.reserved_quantity -= released
            stock.save(update_fields=['reserved_quantity', 'last_updated'])

    def _create_export_receipt_for_order(self, order, user):
        """Tạo phiếu xuất kho tự động từ đơn hàng khi chuyển sang Chờ lấy hàng"""
        from apps.warehouse.repositories import ExportReceiptRepository
        items_data = [
            {
                'product_id': str(item.product_id),
                'quantity': float(item.quantity),
                'unit_price': float(item.unit_price),
                'note': f'Đơn hàng {order.order_code}',
            }
            for item in order.items.select_related('product').all()
        ]
        receipt_data = {
            'note': f'Xuất hàng cho đơn {order.order_code} — KH: {order.customer_name}',
            'sales_order_id': order.id,
        }
        try:
            ExportReceiptRepository.create_with_items(receipt_data, items_data, user)
            return True, None
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f'Lỗi tạo phiếu xuất cho đơn {order.order_code}: {e}')
            return False, 'Không thể tạo phiếu xuất tự động cho đơn hàng.'


    def ready(self):
        from . import report_service