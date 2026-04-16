from decimal import Decimal

from django.test import TestCase

from apps.authentication.models import User
from apps.order.models import SalesOrder
from apps.order.services import SalesOrderService
from apps.product.models import Category, Product
from apps.warehouse.models import ExportReceipt, ProductStock
from apps.warehouse.services import ExportReceiptService


class SalesOrderWorkflowTestCase(TestCase):
    def setUp(self):
        self.sale_user = User.objects.create_user(username='sale01', password='Sale@123', role='SALE', full_name='Sale User')
        self.admin_user = User.objects.create_user(username='admin01', password='Admin@123', role='ADMIN', is_superuser=True, is_staff=True, full_name='Admin User')
        self.ketoan_user = User.objects.create_user(username='ketoan01', password='KeToan@123', role='KE_TOAN', full_name='Ke Toan User')
        self.category = Category.objects.create(name='Vat lieu xay dung')
        self.product = Product.objects.create(name='Thep cay D16', base_price=Decimal('185000'), base_unit='Cay', category=self.category)
        ProductStock.objects.create(product=self.product, quantity=Decimal('100'))
        self.sales_service = SalesOrderService()
        self.export_service = ExportReceiptService()

    def _create_order(self):
        order, errors = self.sales_service.create_order(
            customer_name='Cong ty ABC',
            customer_phone='0901234567',
            note='don test',
            items_data=[{'product_id': str(self.product.id), 'quantity': Decimal('10'), 'unit_price': Decimal('185000')}],
            user=self.sale_user,
        )
        self.assertIsNone(errors)
        return order

    def test_update_to_waiting_creates_linked_export_receipt(self):
        order = self._create_order()

        success, _ = self.sales_service.update_status(order.id, 'WAITING', updated_by=self.admin_user)

        self.assertTrue(success)
        receipt = ExportReceipt.objects.get(sales_order=order)
        self.assertEqual(receipt.status, 'PENDING')
        self.assertEqual(receipt.items.count(), 1)

    def test_approve_export_receipt_moves_order_to_done(self):
        order = self._create_order()
        self.sales_service.update_status(order.id, 'WAITING', updated_by=self.admin_user)
        receipt = ExportReceipt.objects.get(sales_order=order)

        success, _ = self.export_service.approve_receipt(receipt.id, self.ketoan_user)

        self.assertTrue(success)
        order.refresh_from_db()
        self.assertEqual(order.status, 'DONE')
        self.product.stock.refresh_from_db()
        self.assertEqual(self.product.stock.quantity, Decimal('90'))

    def test_reject_export_receipt_returns_order_to_confirmed(self):
        order = self._create_order()
        self.sales_service.update_status(order.id, 'WAITING', updated_by=self.admin_user)
        receipt = ExportReceipt.objects.get(sales_order=order)

        success, _ = self.export_service.reject_receipt(receipt.id, self.ketoan_user, 'thieu hang')

        self.assertTrue(success)
        order.refresh_from_db()
        self.assertEqual(order.status, 'CONFIRMED')

    def test_cancel_order_returns_stock_when_export_already_approved(self):
        order = self._create_order()
        self.sales_service.update_status(order.id, 'WAITING', updated_by=self.admin_user)
        receipt = ExportReceipt.objects.get(sales_order=order)
        self.export_service.approve_receipt(receipt.id, self.ketoan_user)

        success, _ = self.sales_service.update_status(order.id, 'CANCELLED')

        self.assertTrue(success)
        self.product.stock.refresh_from_db()
        self.assertEqual(self.product.stock.quantity, Decimal('100'))
        receipt.refresh_from_db()
        self.assertEqual(receipt.status, 'REJECTED')

    def test_invalid_transition_is_rejected(self):
        order = self._create_order()

        success, message = self.sales_service.update_status(order.id, 'DONE')

        self.assertFalse(success)
        self.assertIn('Không th? chuy?n', message)

    def test_export_approval_is_blocked_when_stock_is_insufficient(self):
        order = self._create_order()
        self.sales_service.update_status(order.id, 'WAITING', updated_by=self.admin_user)
        receipt = ExportReceipt.objects.get(sales_order=order)
        self.product.stock.quantity = Decimal('5')
        self.product.stock.save(update_fields=['quantity'])

        success, message = self.export_service.approve_receipt(receipt.id, self.ketoan_user)

        self.assertFalse(success)
        self.assertIn('tồn kho không đủ', message)
        receipt.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(receipt.status, 'PENDING')
        self.assertEqual(order.status, 'WAITING')

