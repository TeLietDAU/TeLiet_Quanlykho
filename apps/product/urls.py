from django.urls import path
from . import views

# app_name giúp định danh module để gọi trong template: {% url 'product:index' %}
app_name = 'product'

urlpatterns = [
    # 1. Trang danh sách sản phẩm: /product/
    path('', views.ProductListView.as_view(), name='index'),

    # 2. Trang chi tiết sản phẩm: /product/12/
    path('<int:pk>/', views.ProductDetailView.as_view(), name='detail'),

    # 3. Trang thêm mới sản phẩm: /product/create/
    path('create/', views.ProductCreateView.as_view(), name='create'),

    # 4. Trang chỉnh sửa sản phẩm: /product/12/update/
    path('<int:pk>/update/', views.ProductUpdateView.as_view(), name='update'),

    # 5. Trang xóa sản phẩm: /product/12/delete/
    path('<int:pk>/delete/', views.ProductDeleteView.as_view(), name='delete'),
]