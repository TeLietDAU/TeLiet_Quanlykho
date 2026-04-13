from django.db import transaction
from django.db.models import Q
from .models import SalesOrder, SalesOrderItem


class SalesOrderRepository:

    @staticmethod
    def get_all(status=None, search=None):
        queryset = SalesOrder.objects.select_related('created_by').prefetch_related('items__product').all()
        if status:
            queryset = queryset.filter(status=status)
        if search:
            queryset = queryset.filter(
                Q(customer_name__icontains=search) |
                Q(order_code__icontains=search)
            )
        return queryset.order_by('-created_at')

    @staticmethod
    def get_by_id(order_id):
        try:
            return SalesOrder.objects.select_related('created_by').prefetch_related('items__product').get(pk=order_id)
        except SalesOrder.DoesNotExist:
            return None

    @staticmethod
    def get_by_user(user):
        return SalesOrder.objects.select_related('created_by').prefetch_related('items__product').filter(created_by=user)

    @staticmethod
    def get_by_order_code(order_code):
        return SalesOrder.objects.filter(order_code=order_code).first()

    @staticmethod
    def generate_order_code():
        from django.utils import timezone
        date_str = timezone.now().strftime('%Y%m%d')
        count = SalesOrder.objects.filter(
            order_code__startswith=f'DH-{date_str}'
        ).count() + 1
        return f'DH-{date_str}-{count:03d}'

    @staticmethod
    @transaction.atomic
    def create_with_items(order_data, items_data, user):
        """
        Tạo đơn hàng + các dòng sản phẩm.
        Trả về (order, None) nếu thành công.
        Trả về (None, error_list) nếu không đủ tồn kho.
        """
        from apps.warehouse.repositories import ProductStockRepository

        # Kiểm tra tồn kho trước
        errors = []
        for item in items_data:
            stock = ProductStockRepository.get_stock(item['product_id'])
            available = stock.quantity if stock else 0
            if available < item['quantity']:
                from apps.product.models import Product
                try:
                    product = Product.objects.get(pk=item['product_id'])
                    name = product.name
                    unit = product.base_unit
                except Product.DoesNotExist:
                    name = 'Sản phẩm không tồn tại'
                    unit = ''
                errors.append({
                    'product_id': item['product_id'],
                    'product_name': name,
                    'requested': item['quantity'],
                    'available': available,
                    'unit': unit,
                    'message': f'"{name}" chỉ còn {available} {unit}, bạn yêu cầu {item["quantity"]} {unit}.'
                })

        if errors:
            return None, errors

        # Tạo đơn hàng
        order_data['order_code'] = SalesOrderRepository.generate_order_code()
        order_data['created_by'] = user
        order_data['status'] = 'CONFIRMED'

        order = SalesOrder.objects.create(**order_data)

        item_instances = []
        for item in items_data:
            item_instances.append(SalesOrderItem(
                order=order,
                product_id=item['product_id'],
                quantity=item['quantity'],
                unit_price=item.get('unit_price', 0),
            ))

            # KHÔNG trừ kho ngay - chỉ trừ khi phiếu xuất được duyệt
            # Stock sẽ tự động được trừ khi ExportReceipt.approve()
            # from apps.warehouse.models import ProductStock
            # stock, _ = ProductStock.objects.get_or_create(
            #     product_id=item['product_id'],
            #     defaults={'quantity': 0}
            # )
            # stock.quantity -= Decimal(str(item['quantity']))
            # stock.save()

        SalesOrderItem.objects.bulk_create(item_instances)
        return order, None

    @staticmethod
    @transaction.atomic
    def update_status(order, status):
        """Cập nhật trạng thái đơn - nếu hủy + phiếu đã duyệt thì hoàn hàng"""
        old_status = order.status
        order.status = status
        order.save(update_fields=['status'])

        # Nếu chuyển sang CANCELLED → hoàn hàng CHỈ nếu phiếu xuất đã duyệt
        if status == 'CANCELLED':
            from apps.warehouse.models import ExportReceipt
            # Tìm phiếu xuất liên quan
            for receipt in ExportReceipt.objects.filter(note__icontains=order.order_code):
                # Chỉ hoàn khi phiếu đã được duyệt (stock đã bị trừ)
                if receipt.status == 'APPROVED':
                    # Hoàn các sản phẩm từ phiếu xuất
                    from apps.warehouse.models import ProductStock
                    for item in receipt.items.all():
                        stock, _ = ProductStock.objects.get_or_create(
                            product=item.product,
                            defaults={'quantity': 0}
                        )
                        stock.quantity += item.quantity
                        stock.save()
                    # Đổi trạng thái phiếu sang REJECTED (đã hoàn hàng)
                    receipt.status = 'REJECTED'
                    receipt.rejection_note = f'Hoàn hàng do hủy đơn {order.order_code}'
                    receipt.save()

        return order
