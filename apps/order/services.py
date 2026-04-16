from decimal import Decimal

from .repositories import CustomerDebtRepository, SalesOrderRepository


class SalesOrderService:
    VALID_TRANSITIONS = {
        'CONFIRMED': ['WAITING', 'CANCELLED'],
        'WAITING': ['DONE', 'CANCELLED'],
        'DONE': [],
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
        if not customer_name or not customer_name.strip():
            return None, [{'message': 'Vui long nhap ten khach hang.'}]

        if not items_data:
            return None, [{'message': 'Don hang phai co it nhat 1 san pham.'}]

        cleaned_items = []
        for index, item in enumerate(items_data):
            if not item.get('product_id'):
                return None, [{'message': f'Dong {index + 1}: chua chon san pham.'}]
            try:
                quantity = Decimal(str(item.get('quantity', 0)))
            except (ValueError, TypeError, ArithmeticError):
                return None, [{'message': f'Dong {index + 1}: so luong khong hop le.'}]
            if quantity <= 0:
                return None, [{'message': f'Dong {index + 1}: so luong phai lon hon 0.'}]

            item['quantity'] = quantity
            cleaned_items.append(item)

        order_data = {
            'customer_name': customer_name.strip(),
            'customer_phone': customer_phone.strip() if customer_phone else '',
            'note': note or '',
        }
        return SalesOrderRepository.create_with_items(order_data, cleaned_items, user)

    def update_status(self, order_id, new_status, updated_by=None):
        order = SalesOrderRepository.get_by_id(order_id)
        if not order:
            return False, 'Khong tim thay don hang.'

        allowed_transitions = self.VALID_TRANSITIONS.get(order.status, [])
        if new_status not in allowed_transitions:
            labels = {
                'CONFIRMED': 'Da xac nhan',
                'WAITING': 'Cho lay hang',
                'DONE': 'Hoan thanh',
                'CANCELLED': 'Da huy',
            }
            current_label = labels.get(order.status, order.status)
            new_label = labels.get(new_status, new_status)
            return False, f'Khong the chuyen tu "{current_label}" sang "{new_label}".'

        SalesOrderRepository.update_status(order, new_status)

        if new_status == 'WAITING' and updated_by is not None:
            self._create_export_receipt_for_order(order, updated_by)

        return True, 'Cap nhat trang thai thanh cong.'

    def _create_export_receipt_for_order(self, order, user):
        from apps.warehouse.repositories import ExportReceiptRepository

        items_data = [
            {
                'product_id': str(item.product_id),
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'note': f'Don hang {order.order_code}',
            }
            for item in order.items.select_related('product').all()
        ]
        receipt_data = {
            'note': f'Xuat hang cho don {order.order_code} - KH: {order.customer_name}',
            'sales_order': order,
        }
        try:
            ExportReceiptRepository.create_with_items(receipt_data, items_data, user)
        except Exception as exc:
            import logging

            logging.getLogger(__name__).error(
                'Loi tao phieu xuat cho don %s: %s',
                order.order_code,
                exc,
            )


class CustomerDebtService:
    def __init__(self):
        self.repo = CustomerDebtRepository()

    def get_all(self, status=None, search=None):
        return CustomerDebtRepository.get_all(status=status, search_customer=search)

    def get_by_id(self, debt_id):
        return CustomerDebtRepository.get_by_id(debt_id)

    def get_pending(self):
        return CustomerDebtRepository.get_pending_debts()

    def create_debt(self, sales_order, customer_name, remaining_amount, due_date=None, note=None):
        return CustomerDebtRepository.create(
            {
                'sales_order': sales_order,
                'customer_name': customer_name,
                'remaining_amount': remaining_amount,
                'due_date': due_date,
                'note': note or '',
            }
        )

    def mark_paid(self, debt_id):
        debt = CustomerDebtRepository.get_by_id(debt_id)
        if not debt:
            return False, 'Khong tim thay cong no.'
        CustomerDebtRepository.update_status(debt, 'PAID')
        return True, 'Da danh dau thanh toan.'

    def get_stats(self):
        from django.db.models import Sum
        from django.utils import timezone

        from .models import CustomerDebt, SalesOrder

        today = timezone.now().date()
        return {
            'total_orders': SalesOrder.objects.count(),
            'pending_orders': SalesOrder.objects.filter(status='WAITING').count(),
            'total_debt': CustomerDebt.objects.filter(status='PENDING').aggregate(total=Sum('remaining_amount'))['total'] or 0,
            'today_transactions': CustomerDebt.objects.filter(created_at__date=today).count(),
        }
