from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
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
        self.kho_user = User.objects.create_user(username='kho01', password='Kho@123', role='KHO', full_name='Kho User')
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

    def test_update_to_waiting_creates_linked_export_receipt_in_preparing(self):
        order = self._create_order()

        success, _ = self.sales_service.update_status(order.id, 'WAITING', updated_by=self.admin_user)

        self.assertTrue(success)
        receipt = ExportReceipt.objects.get(sales_order=order)
        self.assertEqual(receipt.status, 'PREPARING')
        self.assertEqual(receipt.items.count(), 1)

    def test_mark_picked_moves_order_to_picked_and_deducts_stock(self):
        order = self._create_order()
        self.sales_service.update_status(order.id, 'WAITING', updated_by=self.admin_user)
        receipt = ExportReceipt.objects.get(sales_order=order)
        photo = SimpleUploadedFile('picked.jpg', b'fake-image-bytes', content_type='image/jpeg')

        success, _ = self.export_service.mark_as_picked(receipt.id, self.kho_user, pickup_photo=photo)

        self.assertTrue(success)
        receipt.refresh_from_db()
        order.refresh_from_db()
        self.product.stock.refresh_from_db()
        self.assertEqual(receipt.status, 'PENDING')
        self.assertTrue(receipt.stock_deducted)
        self.assertTrue(bool(receipt.pickup_photo))
        self.assertEqual(order.status, 'PICKED')
        self.assertEqual(self.product.stock.quantity, Decimal('90'))

    def test_approve_after_pick_moves_order_to_done_without_second_stock_deduction(self):
        order = self._create_order()
        self.sales_service.update_status(order.id, 'WAITING', updated_by=self.admin_user)
        receipt = ExportReceipt.objects.get(sales_order=order)
        self.export_service.mark_as_picked(receipt.id, self.kho_user)

        success, _ = self.export_service.approve_receipt(receipt.id, self.ketoan_user)

        self.assertTrue(success)
        order.refresh_from_db()
        self.product.stock.refresh_from_db()
        self.assertEqual(order.status, 'DONE')
        self.assertEqual(self.product.stock.quantity, Decimal('90'))

    def test_reject_after_pick_restores_stock_and_returns_order_to_waiting(self):
        order = self._create_order()
        self.sales_service.update_status(order.id, 'WAITING', updated_by=self.admin_user)
        receipt = ExportReceipt.objects.get(sales_order=order)
        self.export_service.mark_as_picked(receipt.id, self.kho_user)

        success, _ = self.export_service.reject_receipt(receipt.id, self.ketoan_user, 'thieu anh')

        self.assertTrue(success)
        order.refresh_from_db()
        self.product.stock.refresh_from_db()
        receipt.refresh_from_db()
        self.assertEqual(order.status, 'WAITING')
        self.assertEqual(receipt.status, 'REJECTED')
        self.assertEqual(self.product.stock.quantity, Decimal('100'))

    def test_cancel_order_returns_stock_when_goods_already_picked(self):
        order = self._create_order()
        self.sales_service.update_status(order.id, 'WAITING', updated_by=self.admin_user)
        receipt = ExportReceipt.objects.get(sales_order=order)
        self.export_service.mark_as_picked(receipt.id, self.kho_user)

        success, _ = self.sales_service.update_status(order.id, 'CANCELLED')

        self.assertTrue(success)
        self.product.stock.refresh_from_db()
        receipt.refresh_from_db()
        self.assertEqual(self.product.stock.quantity, Decimal('100'))
        self.assertEqual(receipt.status, 'REJECTED')

    def test_invalid_transition_is_rejected(self):
        order = self._create_order()

        success, message = self.sales_service.update_status(order.id, 'DONE')

        self.assertFalse(success)
        self.assertIn('Khong the chuyen', message)

    def test_mark_picked_is_blocked_when_stock_is_insufficient(self):
        order = self._create_order()
        self.sales_service.update_status(order.id, 'WAITING', updated_by=self.admin_user)
        receipt = ExportReceipt.objects.get(sales_order=order)
        self.product.stock.quantity = Decimal('5')
        self.product.stock.save(update_fields=['quantity'])

        success, message = self.export_service.mark_as_picked(receipt.id, self.kho_user)

        self.assertFalse(success)
        self.assertIn('ton kho khong du', message)
        receipt.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(receipt.status, 'PREPARING')
        self.assertEqual(order.status, 'WAITING')
