from django.urls import path
from .views import (
    OrderListView, 
    SalesOrderListView, 
    CustomerDebtListView, 
    WarehouseTransactionListView,
    SalesOrderCreateView,
    CustomerDebtCreateView,
    WarehouseTransactionCreateView
)

app_name = 'order'

urlpatterns = [
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('sales-orders/', SalesOrderListView.as_view(), name='sales_order_list'),
    path('sales-orders/create/', SalesOrderCreateView.as_view(), name='sales_order_create'),
    path('customer-debts/', CustomerDebtListView.as_view(), name='customer_debt_list'),
    path('customer-debts/create/', CustomerDebtCreateView.as_view(), name='customer_debt_create'),
    path('warehouse-transactions/', WarehouseTransactionListView.as_view(), name='warehouse_transaction_list'),
    path('warehouse-transactions/create/', WarehouseTransactionCreateView.as_view(), name='warehouse_transaction_create'),
]
