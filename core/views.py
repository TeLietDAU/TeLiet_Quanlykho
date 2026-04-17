from datetime import datetime, time, timedelta
from decimal import Decimal

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db import connections
from django.db.models import DecimalField, ExpressionWrapper, F, Sum
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
TIME_RANGE_CHOICES = (
    ('today', 'Hôm nay'),
    ('7d', '7 ngày'),
    ('30d', '30 ngày'),
    ('month', 'Tháng này'),
    ('custom', 'Tùy chọn'),
)
TIME_RANGE_LABELS = dict(TIME_RANGE_CHOICES)
DEFAULT_DASHBOARD_RANGE = '7d'
PROCESSING_STATUSES = ('CONFIRMED', 'WAITING')


def _format_decimal_with_dot_grouping(value):
    try:
        return f'{int(value):,}'.replace(',', '.')
    except (TypeError, ValueError):
        return '0'


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


def _line_total_expression():
    return ExpressionWrapper(
        F('quantity') * F('unit_price'),
        output_field=DecimalField(max_digits=24, decimal_places=4),
    )


def _get_revenue_for_orders(order_queryset):
    return (
        SalesOrderItem.objects.filter(order__in=order_queryset, order__status='DONE')
        .aggregate(total=Sum(_line_total_expression()))['total']
        or Decimal('0')
    )


def _get_order_totals_map(order_ids):
    if not order_ids:
        return {}

    totals = (
        SalesOrderItem.objects.filter(order_id__in=order_ids)
        .values('order_id')
        .annotate(total=Sum(_line_total_expression()))
    )
    return {row['order_id']: row['total'] or Decimal('0') for row in totals}


def _get_order_queryset_for_user(user):
    if user.is_superuser or user.role in ('ADMIN', 'KE_TOAN', 'KHO'):
        return SalesOrder.objects.all()
    if user.role == 'SALE':
        return SalesOrder.objects.filter(created_by=user)
    return SalesOrder.objects.all()


def _parse_date_input(raw_value):
    if not raw_value:
        return None

    try:
        return datetime.strptime(raw_value, '%Y-%m-%d').date()
    except ValueError:
        return None


def _resolve_dashboard_time_filter(request):
    now = timezone.localtime()
    range_key = request.GET.get('range', DEFAULT_DASHBOARD_RANGE).strip().lower()
    if range_key not in TIME_RANGE_LABELS:
        range_key = DEFAULT_DASHBOARD_RANGE

    start_date_value = ''
    end_date_value = ''
    tz = timezone.get_current_timezone()

    if range_key == 'today':
        start_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_dt = now
    elif range_key == '7d':
        start_dt = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_dt = now
    elif range_key == '30d':
        start_dt = (now - timedelta(days=29)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_dt = now
    elif range_key == 'month':
        start_dt = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_dt = now
    else:
        start_date = _parse_date_input(request.GET.get('start_date', '').strip())
        end_date = _parse_date_input(request.GET.get('end_date', '').strip())

        if not start_date:
            start_date = now.date() - timedelta(days=6)
        if not end_date:
            end_date = now.date()
        if end_date < start_date:
            start_date, end_date = end_date, start_date

        start_dt = timezone.make_aware(datetime.combine(start_date, time.min), tz)
        end_dt = timezone.make_aware(datetime.combine(end_date + timedelta(days=1), time.min), tz)
        start_date_value = start_date.isoformat()
        end_date_value = end_date.isoformat()

    if end_dt <= start_dt:
        end_dt = start_dt + timedelta(days=1)

    period_delta = end_dt - start_dt
    previous_start = start_dt - period_delta
    previous_end = start_dt

    if range_key == 'custom':
        period_label = f"{start_dt.strftime('%d/%m/%Y')} - {(end_dt - timedelta(microseconds=1)).strftime('%d/%m/%Y')}"
    else:
        period_label = TIME_RANGE_LABELS.get(range_key, 'Khoảng thời gian')

    return {
        'range_key': range_key,
        'start_dt': start_dt,
        'end_dt': end_dt,
        'previous_start': previous_start,
        'previous_end': previous_end,
        'period_label': period_label,
        'compare_label': 'So với kỳ trước cùng độ dài',
        'start_date': start_date_value,
        'end_date': end_date_value,
    }


def _collect_period_metrics(order_queryset):
    total_orders = order_queryset.count()
    processing_orders = order_queryset.filter(status__in=PROCESSING_STATUSES).count()
    done_orders = order_queryset.filter(status='DONE').count()
    revenue = _get_revenue_for_orders(order_queryset)
    completion_rate = (done_orders * 100 / total_orders) if total_orders else 0.0

    return {
        'total_orders': total_orders,
        'revenue': revenue,
        'processing_orders': processing_orders,
        'done_orders': done_orders,
        'completion_rate': completion_rate,
    }


def _build_dashboard_stats(base_queryset, time_filter):
    current_queryset = base_queryset.filter(
        created_at__gte=time_filter['start_dt'],
        created_at__lt=time_filter['end_dt'],
    )
    previous_queryset = base_queryset.filter(
        created_at__gte=time_filter['previous_start'],
        created_at__lt=time_filter['previous_end'],
    )

    current_metrics = _collect_period_metrics(current_queryset)
    previous_metrics = _collect_period_metrics(previous_queryset)

    total_orders_change = _calculate_change(current_metrics['total_orders'], previous_metrics['total_orders'])
    revenue_change = _calculate_change(float(current_metrics['revenue']), float(previous_metrics['revenue']))
    processing_change = _calculate_improvement_for_lower_better(
        current_metrics['processing_orders'],
        previous_metrics['processing_orders'],
    )
    completion_change = _calculate_change(
        current_metrics['completion_rate'],
        previous_metrics['completion_rate'],
    )

    stats = [
        {
            'label': 'Tổng đơn hàng',
            'value': _format_decimal_with_dot_grouping(current_metrics['total_orders']),
            'change': _format_change(total_orders_change),
            'is_positive': total_orders_change >= 0,
        },
        {
            'label': 'Doanh thu tháng',
            'value': _format_currency_short(current_metrics['revenue']),
            'change': _format_change(revenue_change),
            'is_positive': revenue_change >= 0,
        },
        {
            'label': 'Đang xử lý',
            'value': _format_decimal_with_dot_grouping(current_metrics['processing_orders']),
            'change': _format_change(processing_change),
            'is_positive': processing_change >= 0,
        },
        {
            'label': 'Tỷ lệ hoàn thành',
            'value': f"{current_metrics['completion_rate']:.1f}%",
            'change': _format_change(completion_change),
            'is_positive': completion_change >= 0,
        },
    ]
    return stats


def _build_time_buckets(start_dt, end_dt, range_key):
    if range_key == 'today':
        step = timedelta(hours=2)
    elif range_key == 'custom':
        total_days = max(1, (end_dt.date() - start_dt.date()).days)
        step = timedelta(days=7) if total_days > 45 else timedelta(days=1)
    else:
        step = timedelta(days=1)

    buckets = []
    cursor = start_dt
    while cursor < end_dt:
        next_cursor = min(cursor + step, end_dt)
        local_start = timezone.localtime(cursor)
        if step >= timedelta(days=7):
            local_end = timezone.localtime(next_cursor - timedelta(microseconds=1))
            label = f"{local_start.strftime('%d/%m')}-{local_end.strftime('%d/%m')}"
        elif step >= timedelta(days=1):
            label = local_start.strftime('%d/%m')
        else:
            label = local_start.strftime('%H:%M')

        buckets.append({'start': cursor, 'end': next_cursor, 'label': label})
        cursor = next_cursor

    return buckets


def _build_chart_points(labels, values, formatter):
    if not labels:
        return []

    numeric_values = []
    for value in values:
        try:
            numeric_values.append(float(value))
        except (TypeError, ValueError):
            numeric_values.append(0.0)

    max_value = max(numeric_values) if numeric_values else 0.0
    points = []
    for label, value, numeric in zip(labels, values, numeric_values):
        if max_value > 0:
            height = max(10, int(round((numeric / max_value) * 100)))
        else:
            height = 10

        points.append(
            {
                'label': label,
                'value': formatter(value),
                'height': height,
            }
        )

    return points


def _build_mini_charts(base_queryset, time_filter):
    buckets = _build_time_buckets(
        time_filter['start_dt'],
        time_filter['end_dt'],
        time_filter['range_key'],
    )
    if not buckets:
        return []

    orders = [0] * len(buckets)
    processing = [0] * len(buckets)
    done = [0] * len(buckets)
    revenue = [Decimal('0')] * len(buckets)

    rows = list(base_queryset.filter(
        created_at__gte=time_filter['start_dt'],
        created_at__lt=time_filter['end_dt'],
    ).values('id', 'created_at', 'status'))
    done_order_ids = [row['id'] for row in rows if row['status'] == 'DONE']
    order_totals = _get_order_totals_map(done_order_ids)

    for row in rows:
        created_at = row['created_at']
        for index, bucket in enumerate(buckets):
            if bucket['start'] <= created_at < bucket['end']:
                orders[index] += 1
                if row['status'] in PROCESSING_STATUSES:
                    processing[index] += 1
                if row['status'] == 'DONE':
                    done[index] += 1
                    revenue[index] += order_totals.get(row['id'], Decimal('0'))
                break

    completion = []
    for index, total in enumerate(orders):
        completion.append((done[index] * 100 / total) if total else 0.0)

    labels = [bucket['label'] for bucket in buckets]
    total_orders = sum(orders)
    total_revenue = sum(revenue, Decimal('0'))
    total_processing = sum(processing)
    total_done = sum(done)
    overall_completion = (total_done * 100 / total_orders) if total_orders else 0.0

    return [
        {
            'title': 'Đơn hàng',
            'subtitle': 'Tổng đơn trong kỳ',
            'value': _format_decimal_with_dot_grouping(total_orders),
            'color': '#3b82f6',
            'points': _build_chart_points(
                labels,
                orders,
                lambda value: _format_decimal_with_dot_grouping(value),
            ),
            'start_label': labels[0],
            'end_label': labels[-1],
        },
        {
            'title': 'Doanh thu',
            'subtitle': 'Đơn hoàn thành',
            'value': _format_currency_short(total_revenue),
            'color': '#22c55e',
            'points': _build_chart_points(labels, revenue, _format_currency_short),
            'start_label': labels[0],
            'end_label': labels[-1],
        },
        {
            'title': 'Đang xử lý',
            'subtitle': 'CONFIRMED + WAITING',
            'value': _format_decimal_with_dot_grouping(total_processing),
            'color': '#f59e0b',
            'points': _build_chart_points(
                labels,
                processing,
                lambda value: _format_decimal_with_dot_grouping(value),
            ),
            'start_label': labels[0],
            'end_label': labels[-1],
        },
        {
            'title': 'Hoàn thành',
            'subtitle': 'Tỷ lệ theo mốc thời gian',
            'value': f'{overall_completion:.1f}%',
            'color': '#a855f7',
            'points': _build_chart_points(labels, completion, lambda value: f'{value:.1f}%'),
            'start_label': labels[0],
            'end_label': labels[-1],
        },
    ]


@login_required
def dashboard_view(request):
    base_queryset = _get_order_queryset_for_user(request.user)
    time_filter = _resolve_dashboard_time_filter(request)
    stats = _build_dashboard_stats(base_queryset, time_filter)
    chart_cards = _build_mini_charts(base_queryset, time_filter)
    time_filter_options = [
        {'value': value, 'label': label}
        for value, label in TIME_RANGE_CHOICES
    ]

    context = {
        **_base_context(request),
        'today': timezone.localtime(),
        'stats': stats,
        'chart_cards': chart_cards,
        'time_filter': time_filter,
        'time_filter_options': time_filter_options,
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