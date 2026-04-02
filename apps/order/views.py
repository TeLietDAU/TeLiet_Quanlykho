from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .repositories import SalesOrderRepository
from .models import SalesOrder, CustomerDebt, WarehouseTransaction

class OrderListView(LoginRequiredMixin, View):
    def get(self, request):
        search_query = request.GET.get('search', '')
        status_filter = request.GET.get('status', '')
        
        # Lấy tất cả đơn hàng
        orders = SalesOrderRepository.get_all(status=status_filter if status_filter else None, search=search_query if search_query else None)
        
        return render(request, 'order/order_list.html', {
            'orders': orders,
            'selected_status': status_filter,
            'selected_search': search_query,
        })

class SalesOrderListView(LoginRequiredMixin, View):
    def get(self, request):
        search_query = request.GET.get('search', '')
        status_filter = request.GET.get('status', '')
        
        orders = SalesOrderRepository.get_all(status=status_filter if status_filter else None, search=search_query if search_query else None)
        
        return render(request, 'order/sales_order_list.html', {
            'orders': orders,
            'selected_status': status_filter,
            'selected_search': search_query,
        })

class CustomerDebtListView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'order/customer_debt_list.html', {})

class WarehouseTransactionListView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'order/warehouse_transaction_list.html', {})

class SalesOrderCreateView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'order/sales_order_create.html')
    
    def post(self, request):
        try:
            order = SalesOrder.objects.create(
                order_code=request.POST.get('order_code'),
                customer_name=request.POST.get('customer_name'),
                created_by=request.user,
                order_date=request.POST.get('order_date'),
                total_amount=float(request.POST.get('total_amount', 0)),
                status=request.POST.get('status')
            )
            messages.success(request, 'Đơn hàng đã được tạo thành công!')
            return redirect('order:sales_order_list')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
            return render(request, 'order/sales_order_create.html')

class CustomerDebtCreateView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'order/customer_debt_create.html')
    
    def post(self, request):
        try:
            debt = CustomerDebt.objects.create(
                customer_name=request.POST.get('customer_name'),
                remaining_amount=float(request.POST.get('remaining_amount', 0)),
                due_date=request.POST.get('due_date'),
                status=request.POST.get('status'),
                notes=request.POST.get('notes', '')
            )
            messages.success(request, 'Nợ khách hàng đã được thêm thành công!')
            return redirect('order:customer_debt_list')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
            return render(request, 'order/customer_debt_create.html')

class WarehouseTransactionCreateView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'order/warehouse_transaction_create.html')
    
    def post(self, request):
        try:
            transaction = WarehouseTransaction.objects.create(
                code=request.POST.get('code'),
                product=request.POST.get('product'),
                warehouse=request.POST.get('warehouse'),
                quantity=int(request.POST.get('quantity', 0)),
                transaction_type=request.POST.get('transaction_type'),
                transaction_date=request.POST.get('transaction_date'),
                created_by=request.user,
                notes=request.POST.get('notes', '')
            )
            messages.success(request, 'Giao dịch kho đã được tạo thành công!')
            return redirect('order:warehouse_transaction_list')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
            return render(request, 'order/warehouse_transaction_create.html')
