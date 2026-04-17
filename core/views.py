from datetime import timedelta
from decimal import Decimal

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db import connections
from django.db.models import DecimalField, ExpressionWrapper, F, Q, Sum
from django.db.utils import OperationalError
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone

# --- IMPORT TẦNG SERVICE ---
from apps.authentication.services import UserService
from apps.order.models import SalesOrder, SalesOrderItem
from apps.product.models import ProductUnit, Product # Mở comment và đảm bảo path đúng

# ==========================================
# 1. HỆ THỐNG & SỨC KHỎE (HEALTH CHECK)
# ==========================================
def health_check(request):
    health_status = {"api": "ok", "database": "ok"}
    status_code = 200
    try:
        db_conn = connections['default']
        db_conn.cursor()
    except OperationalError:
        health_status["database"] = "disconnected"
        status_code = 503
    except Exception as e:
        health_status["database"] = "error"
        health_status["details"] = str(e)
        status_code = 500
    return JsonResponse(health_status, status=status_code)

# ==========================================
# 2. XÁC THỰC NGƯỜI DÙNG (KẾT NỐI SERVICE)
# ==========================================
def login_view(request):
    # Nếu đã đăng nhập rồi thì vào thẳng Dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Gọi Service để xử lý xác thực
        auth_service = UserService()
        user = auth_service.login_service(request, username, password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Chào mừng trở lại, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng hoặc tài khoản bị khóa.')
            
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# ==========================================
# 3. HÀM BỔ TRỢ (SỬ DỤNG TRƯỜNG ROLE MỚI)
# ==========================================
def _base_context(request):
    """Lấy thông tin hiển thị dựa trên Custom User Model."""
    user = request.user
    role_name = "Thành viên"
    
    if user.is_authenticated:
        # Tận dụng trường 'role' trực tiếp từ Model User bạn đã tạo
        roles_map = {
            'ADMIN': 'Quản trị viên',
            'KHO': 'Thủ kho',
            'SALE': 'Nhân viên bán hàng',
            'KE_TOAN': 'Kế toán',
        }
        # Lấy tên hiển thị Tiếng Việt từ Map, nếu không có thì dùng giá trị gốc
        current_role = 'ADMIN' if user.is_superuser else user.role
        role_name = roles_map.get(current_role, current_role)

    return {
        'user_full_name': getattr(user, 'full_name', user.username) if user.is_authenticated else "Khách",
        'user_initial': user.username[0].upper() if user.is_authenticated else '?',
        'user_role': role_name,
    }

# ==========================================
# 4. CÁC TRANG TỔNG QUAN (DASHBOARD)
# ==========================================
DASHBOARD_PAGE_SIZE = 5
ALLOWED_ORDER_STATUSES = {'CONFIRMED', 'WAITING', 'DONE', 'CANCELLED'}
ORDER_STATUS_BADGE = {
    'CONFIRMED': ('pending', '#3b82f6'),
    'WAITING': ('processing', '#f59e0b'),
    'DONE': ('done', '#22c55e'),
    'CANCELLED': ('cancel', '#ef4444'),
}


def _format_decimal_with_dot_grouping(value):
    try:
        return f'{int(value):,}'.replace(',', '.')
    except (TypeError, ValueError):
        return '0'


def _format_vnd(value):
    try:
        amount = Decimal(value or 0)
    except Exception:
        amount = Decimal('0')
    return f"{_format_decimal_with_dot_grouping(amount)}đ"


def _format_currency_short(value):
    try:
        amount = float(value or 0)
    except (TypeError, ValueError):
        amount = 0.0

    abs_amount = abs(amount)
    if abs_amount >= 1_000_000_000:
        return f'{amount / 1_000_000_000:.1f}B đ'
    if abs_amount >= 1_000_000:
        return f'{amount / 1_000_000:.1f}M đ'
    if abs_amount >= 1_000:
        return f'{amount / 1_000:.1f}K đ'
    return f'{amount:.0f} đ'


def _format_change(value):
    return f'{value:+.1f}%'


def _calculate_change(current, previous):
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return ((current - previous) / previous) * 100


def _calculate_improvement_for_lower_better(current, previous):
    if previous == 0:
        return -100.0 if current > 0 else 0.0
    return ((previous - current) / previous) * 100


def _build_pagination_items(current_page, total_pages, window=1):
    if total_pages <= 0:
        return []

    pages = {1, total_pages}
    for page_num in range(current_page - window, current_page + window + 1):
        if 1 <= page_num <= total_pages:
            pages.add(page_num)

    sorted_pages = sorted(pages)
    items = []
    previous = None
    for page_num in sorted_pages:
        if previous is not None and page_num - previous > 1:
            items.append('ellipsis')
        items.append(page_num)
        previous = page_num

    return items


def _get_order_queryset_for_user(user):
    if user.is_superuser or user.role in ('ADMIN', 'KE_TOAN', 'KHO'):
        return SalesOrder.objects.all()
    if user.role == 'SALE':
        return SalesOrder.objects.filter(created_by=user)
    return SalesOrder.objects.all()


def _get_product_summary(order, max_items=2):
    product_names = [item.product.name for item in order.items.all() if item.product]
    if not product_names:
        return '—'
    if len(product_names) <= max_items:
        return ', '.join(product_names)
    return f"{', '.join(product_names[:max_items])} +{len(product_names) - max_items}"


def _get_monthly_revenue(order_queryset):
    line_total = ExpressionWrapper(
        F('quantity') * F('unit_price'),
        output_field=DecimalField(max_digits=24, decimal_places=4),
    )
    return (
        SalesOrderItem.objects.filter(order__in=order_queryset, order__status='DONE')
        .aggregate(total=Sum(line_total))['total']
        or Decimal('0')
    )


def _build_dashboard_stats(base_queryset):
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    previous_month_end = month_start - timedelta(microseconds=1)
    previous_month_start = previous_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    current_month_orders = base_queryset.filter(created_at__gte=month_start)
    previous_month_orders = base_queryset.filter(created_at__gte=previous_month_start, created_at__lt=month_start)

    current_total_orders = current_month_orders.count()
    previous_total_orders = previous_month_orders.count()

    current_revenue = _get_monthly_revenue(current_month_orders)
    previous_revenue = _get_monthly_revenue(previous_month_orders)

    current_processing = current_month_orders.filter(status__in=('CONFIRMED', 'WAITING')).count()
    previous_processing = previous_month_orders.filter(status__in=('CONFIRMED', 'WAITING')).count()

    current_done = current_month_orders.filter(status='DONE').count()
    previous_done = previous_month_orders.filter(status='DONE').count()
    current_completion_rate = (current_done * 100 / current_total_orders) if current_total_orders else 0.0
    previous_completion_rate = (previous_done * 100 / previous_total_orders) if previous_total_orders else 0.0

    total_orders_change = _calculate_change(current_total_orders, previous_total_orders)
    revenue_change = _calculate_change(float(current_revenue), float(previous_revenue))
    processing_change = _calculate_improvement_for_lower_better(current_processing, previous_processing)
    completion_change = _calculate_change(current_completion_rate, previous_completion_rate)

    return [
        {
            'label': 'Tổng đơn hàng',
            'value': _format_decimal_with_dot_grouping(current_total_orders),
            'change': _format_change(total_orders_change),
            'is_positive': total_orders_change >= 0,
        },
        {
            'label': 'Doanh thu tháng',
            'value': _format_currency_short(current_revenue),
            'change': _format_change(revenue_change),
            'is_positive': revenue_change >= 0,
        },
        {
            'label': 'Đang xử lý',
            'value': _format_decimal_with_dot_grouping(current_processing),
            'change': _format_change(processing_change),
            'is_positive': processing_change >= 0,
        },
        {
            'label': 'Tỷ lệ hoàn thành',
            'value': f'{current_completion_rate:.1f}%',
            'change': _format_change(completion_change),
            'is_positive': completion_change >= 0,
        },
    ]


@login_required
def dashboard_view(request):
    base_queryset = _get_order_queryset_for_user(request.user)
    stats = _build_dashboard_stats(base_queryset)

    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip().upper()
    page_number = request.GET.get('page', 1)

    orders_queryset = (
        base_queryset.select_related('created_by')
        .prefetch_related('items__product')
        .order_by('-created_at')
    )

    if search_query:
        orders_queryset = orders_queryset.filter(
            Q(order_code__icontains=search_query)
            | Q(customer_name__icontains=search_query)
            | Q(items__product__name__icontains=search_query)
        ).distinct()

    if status_filter in ALLOWED_ORDER_STATUSES:
        orders_queryset = orders_queryset.filter(status=status_filter)
    else:
        status_filter = ''

    paginator = Paginator(orders_queryset, DASHBOARD_PAGE_SIZE)
    page_obj = paginator.get_page(page_number)

    orders = []
    for order in page_obj.object_list:
        badge_class, dot_color = ORDER_STATUS_BADGE.get(order.status, ('pending', '#3b82f6'))
        orders.append(
            {
                'id': str(order.id),
                'ma_don': order.order_code,
                'khach_hang': order.customer_name,
                'vat_lieu': _get_product_summary(order),
                'ngay_tao': timezone.localtime(order.created_at).strftime('%d/%m/%Y'),
                'trang_thai': order.get_status_display(),
                'trang_thai_class': badge_class,
                'dot_color': dot_color,
                'tong_tien': _format_vnd(order.total_amount),
            }
        )

    pagination_items = _build_pagination_items(page_obj.number, paginator.num_pages, window=1)

    context = {
        **_base_context(request),
        'today': timezone.localtime(),
        'stats': stats,
        'orders': orders,
        'total_orders': paginator.count,
        'search_query': search_query,
        'status_filter': status_filter,
        'paginator': paginator,
        'page_obj': page_obj,
        'pagination_items': pagination_items,
    }
    return render(request, 'dashboard.html', context)

# ==========================================
# 5. QUẢN LÝ NGHIỆP VỤ (DÙNG LOGIN_REQUIRED)
# ==========================================
@login_required
def product_view(request):
    return render(request, 'Product.html', _base_context(request))

@login_required
def units_view(request):
    """Trang hiển thị Đơn vị quy đổi (AJAX)"""
    # Lấy dữ liệu thực từ DB để truyền cho giao diện AJAX
    unit_list = ProductUnit.objects.select_related('product').all()
    units_data = [{
        'id': str(u.id),
        'unit_name': u.unit_name,
        'conversion_rate': float(u.conversion_rate),
        'product_name': u.product.name,
        'base_unit': u.product.base_unit
    } for u in unit_list]

    product_list = Product.objects.all()
    Product_data = [{
        'id': str(p.id),
        'name': p.name,
        'base_unit': p.base_unit
    } for p in product_list]

    context = {
        **_base_context(request),
        'units_json': units_data,
        'Product_json': Product_data,
    }
    return render(request, 'units.html', context)


@login_required
def accounts_view(request):
    return render(request, 'accounts.html', _base_context(request))