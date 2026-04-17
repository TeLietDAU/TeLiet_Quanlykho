import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View

from apps.product.models import Product

from .models import SalesOrder, SalesOrderItem
from .services import SalesOrderService


PAGE_SIZE = 5


def _products_json():
    products = Product.objects.select_related('category').all().order_by('name')
    return [
        {
            'id': str(product.id),
            'name': product.name,
            'base_unit': product.base_unit,
            'base_price': float(product.base_price),
            'category': product.category.name if product.category else '',
        }
        for product in products
    ]


def _stocks_json():
    from apps.warehouse.repositories import ProductStockRepository

    stocks = ProductStockRepository.get_all()
    return {str(stock.product_id): float(stock.quantity) for stock in stocks}


def _parse_items_from_post(post_data):
    items = []
    index = 0
    while True:
        product_id = post_data.get(f'product_id_{index}')
        if product_id is None:
            break
        if product_id:
            items.append(
                {
                    'product_id': product_id,
                    'quantity': post_data.get(f'quantity_{index}', 0),
                    'unit_price': post_data.get(f'unit_price_{index}', 0),
                    'note': post_data.get(f'item_note_{index}', ''),
                }
            )
        index += 1
    return items


def _get_sales_order_stats():
    today = timezone.now().date()
    return {
        'total_orders': SalesOrder.objects.count(),
        'pending_orders': SalesOrder.objects.filter(status='WAITING').count(),
        'total_items': SalesOrderItem.objects.aggregate(total=Sum('quantity'))['total'] or 0,
        'today_transactions': SalesOrder.objects.filter(created_at__date=today).count(),
    }


class SalesOrderListView(LoginRequiredMixin, View):
    def get(self, request):
        service = SalesOrderService()
        user = request.user

        if user.role in ('KE_TOAN', 'ADMIN'):
            orders = service.get_all()
        elif user.role == 'SALE':
            orders = service.get_by_user(user)
        else:
            orders = service.get_all()

        status_filter = request.GET.get('status', '')
        search_query = request.GET.get('search', '')
        page_number = request.GET.get('page', 1)

        if status_filter:
            orders = orders.filter(status=status_filter)

        if search_query:
            orders = orders.filter(
                Q(customer_name__icontains=search_query) | Q(order_code__icontains=search_query)
            )

        paginator = Paginator(orders, PAGE_SIZE)
        page_obj = paginator.get_page(page_number)

        return render(
            request,
            'order/sales_order_list.html',
            {
                'orders': page_obj,
                'page_obj': page_obj,
                'paginator': paginator,
                'products_json': json.dumps(_products_json(), ensure_ascii=False),
                'stocks_json': json.dumps(_stocks_json()),
                'user_role': 'ADMIN' if user.is_superuser else user.role,
                'status_filter': status_filter,
                'search_query': search_query,
                'stats': _get_sales_order_stats(),
                'valid_transitions_json': json.dumps(SalesOrderService.VALID_TRANSITIONS),
            },
        )

    def post(self, request):
        user = request.user
        action = request.POST.get('action', '')

        if action == 'update_status':
            if user.role == 'SALE' and not user.is_superuser:
                messages.error(request, 'Ban khong co quyen cap nhat trang thai don hang.')
                return redirect('order:sales_list')

            order_id = request.POST.get('order_id')
            new_status = request.POST.get('status')

            if new_status not in ['CONFIRMED', 'WAITING', 'DONE', 'CANCELLED']:
                messages.error(request, 'Trang thai khong hop le.')
                return redirect('order:sales_list')

            success, message = SalesOrderService().update_status(order_id, new_status, updated_by=user)
            if success:
                if new_status == 'WAITING':
                    messages.success(request, f'{message} Phieu xuat kho da duoc tao tu dong va dang cho duyet.')
                else:
                    messages.success(request, message)
            else:
                messages.error(request, message)
            return redirect('order:sales_list')

        if user.role not in ('SALE', 'ADMIN') and not user.is_superuser:
            messages.error(request, 'Ban khong co quyen tao don hang.')
            return redirect('order:sales_list')

        customer_name = request.POST.get('customer_name', '')
        customer_phone = request.POST.get('customer_phone', '')
        note = request.POST.get('note', '')
        items_data = _parse_items_from_post(request.POST)

        order, errors = SalesOrderService().create_order(
            customer_name,
            customer_phone,
            note,
            items_data,
            user,
        )

        if order:
            messages.success(
                request,
                f'Don hang {order.order_code} da duoc tao. Chuyen sang trang thai cho lay hang de tao phieu xuat.',
            )
        else:
            for error in errors:
                messages.error(request, error['message'])

        return redirect('order:sales_list')


class SalesOrderDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        order = SalesOrderService().get_by_id(pk)
        if not order:
            messages.error(request, 'Khong tim thay don hang.')
            return redirect('order:sales_list')

        return render(
            request,
            'order/sales_order_detail.html',
            {
                'order': order,
                'user_role': 'ADMIN' if request.user.is_superuser else request.user.role,
                'valid_transitions': SalesOrderService.VALID_TRANSITIONS.get(order.status, []),
            },
        )
