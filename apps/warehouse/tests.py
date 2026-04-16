from decimal import Decimal
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase
from openpyxl import Workbook

from apps.authentication.models import User
from apps.product.models import Category, Product
from apps.product.serializers import ProductSerializer
from apps.order.models import SalesOrder
from apps.warehouse.models import ExportReceipt, ImportReceipt, ProductStock
from apps.warehouse.services import ExportReceiptService, ImportReceiptService, StockService


class WarehouseExcelWorkflowTestCase(TestCase):
    def setUp(self):
        self.kho_user = User.objects.create_user(username='kho01', password='Kho@123', role='KHO', full_name='Kho User')
        self.ketoan_user = User.objects.create_user(username='ketoan01', password='KeToan@123', role='KE_TOAN', full_name='Ke Toan User')
        self.sale_user = User.objects.create_user(username='sale01', password='Sale@123', role='SALE', full_name='Sale User')
        self.category = Category.objects.create(name='Vat lieu')
        self.product = Product.objects.create(name='Xi mang Portland', base_price=Decimal('50000'), base_unit='Bao', category=self.category)
        self.product2 = Product.objects.create(name='Gach nung', base_price=Decimal('3000'), base_unit='Cuc', category=self.category)

    def _build_excel_file(self, rows):
        workbook = Workbook()
        sheet = workbook.active
        sheet.append(['receipt_code', 'product_id', 'product_name', 'quantity', 'unit_price', 'item_note', 'receipt_note', 'sales_order_code'])
        for row in rows:
            sheet.append(row)
        output = BytesIO()
        workbook.save(output)
        output.seek(0)
        return SimpleUploadedFile('receipts.xlsx', output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    def test_import_excel_creates_pending_import_receipt(self):
        file_obj = self._build_excel_file([
            ['', '', self.product.name, 12, 50000, 'dong 1', 'nhap lo A', ''],
            ['', '', self.product2.name, 20, 3000, 'dong 2', 'nhap lo A', ''],
        ])

        receipts = ImportReceiptService().import_receipts_from_excel(file_obj, self.kho_user)

        self.assertEqual(len(receipts), 1)
        receipt = receipts[0]
        self.assertEqual(receipt.status, 'PENDING')
        self.assertEqual(receipt.items.count(), 2)
        self.assertIsNone(ProductStock.objects.filter(product=self.product).first())

    def test_approve_imported_import_receipt_updates_stock(self):
        file_obj = self._build_excel_file([
            ['', '', self.product.name, 12, 50000, '', 'nhap lo A', ''],
        ])
        receipt = ImportReceiptService().import_receipts_from_excel(file_obj, self.kho_user)[0]

        success, _ = ImportReceiptService().approve_receipt(receipt.id, self.ketoan_user)

        self.assertTrue(success)
        stock = ProductStock.objects.get(product=self.product)
        self.assertEqual(stock.quantity, Decimal('12'))

    def test_sale_cannot_approve_import_receipt(self):
        file_obj = self._build_excel_file([
            ['', '', self.product.name, 12, 50000, '', 'nhap lo A', ''],
        ])
        receipt = ImportReceiptService().import_receipts_from_excel(file_obj, self.kho_user)[0]

        success, message = ImportReceiptService().approve_receipt(receipt.id, self.sale_user)

        self.assertFalse(success)
        self.assertIn('khong co quyen', message.lower())

    def test_import_excel_creates_pending_export_receipt_without_stock_change(self):
        ProductStock.objects.create(product=self.product, quantity=Decimal('40'))
        file_obj = self._build_excel_file([
            ['', '', self.product.name, 10, 50000, 'dong xuat', 'xuat lo A', ''],
        ])

        receipts = ExportReceiptService().import_receipts_from_excel(file_obj, self.kho_user)

        self.assertEqual(len(receipts), 1)
        receipt = receipts[0]
        self.assertEqual(receipt.status, 'PENDING')
        self.product.stock.refresh_from_db()
        self.assertEqual(self.product.stock.quantity, Decimal('40'))

    def test_approve_imported_export_receipt_updates_order_to_done(self):
        ProductStock.objects.create(product=self.product, quantity=Decimal('40'))
        order = SalesOrder.objects.create(
            order_code='DH-20260414-001',
            customer_name='Khach A',
            customer_phone='0901234567',
            created_by=self.sale_user,
            status='WAITING',
        )
        order.items.create(product=self.product, quantity=Decimal('10'), unit_price=Decimal('50000'))
        file_obj = self._build_excel_file([
            ['', '', self.product.name, 10, 50000, 'xuat', 'xuat theo don', order.order_code],
        ])

        receipt = ExportReceiptService().import_receipts_from_excel(file_obj, self.kho_user)[0]
        success, _ = ExportReceiptService().approve_receipt(receipt.id, self.ketoan_user)

        self.assertTrue(success)
        order.refresh_from_db()
        self.assertEqual(order.status, 'DONE')
        self.product.stock.refresh_from_db()
        self.assertEqual(self.product.stock.quantity, Decimal('30'))

    def test_sale_cannot_approve_export_receipt(self):
        ProductStock.objects.create(product=self.product, quantity=Decimal('40'))
        file_obj = self._build_excel_file([
            ['', '', self.product.name, 10, 50000, 'dong xuat', 'xuat lo A', ''],
        ])
        receipt = ExportReceiptService().import_receipts_from_excel(file_obj, self.kho_user)[0]

        success, message = ExportReceiptService().approve_receipt(receipt.id, self.sale_user)

        self.assertFalse(success)
        self.assertIn('khong co quyen', message.lower())

    def test_import_excel_export_receipt_moves_linked_order_to_waiting(self):
        ProductStock.objects.create(product=self.product, quantity=Decimal('40'))
        order = SalesOrder.objects.create(
            order_code='DH-20260414-002',
            customer_name='Khach B',
            customer_phone='0901234568',
            created_by=self.sale_user,
            status='CONFIRMED',
        )
        order.items.create(product=self.product, quantity=Decimal('8'), unit_price=Decimal('50000'))
        file_obj = self._build_excel_file([
            ['', '', self.product.name, 8, 50000, 'xuat', 'xuat theo don', order.order_code],
        ])

        receipt = ExportReceiptService().import_receipts_from_excel(file_obj, self.kho_user)[0]

        order.refresh_from_db()
        self.assertEqual(receipt.sales_order_id, order.id)
        self.assertEqual(order.status, 'WAITING')

    def test_product_serializer_returns_stock_fields(self):
        ProductStock.objects.create(product=self.product, quantity=Decimal('9'))

        payload = ProductSerializer(self.product).data

        self.assertEqual(payload['stock_status'], 'LOW')
        self.assertEqual(payload['stock_status_label'], 'S?p h?t')
        self.assertEqual(str(payload['stock_quantity']), '9.00')

    def test_stock_service_includes_products_without_stock_record(self):
        rows = StockService().get_all_stocks()
        row = next(item for item in rows if item['product'].id == self.product.id)
        self.assertEqual(row['quantity'], Decimal('0'))
        self.assertEqual(row['stock_status_label'], 'H?t hàng')

    def test_seed_command_creates_balanced_demo_data(self):
        call_command('seed_inventory_demo')

        self.assertEqual(SalesOrder.objects.count(), 20)
        self.assertEqual(ImportReceipt.objects.count(), 15)
        self.assertEqual(ExportReceipt.objects.count(), 15)
        self.assertEqual(SalesOrder.objects.filter(status='CONFIRMED').count(), 5)
        self.assertEqual(SalesOrder.objects.filter(status='WAITING').count(), 7)
        self.assertEqual(SalesOrder.objects.filter(status='DONE').count(), 6)
        self.assertEqual(SalesOrder.objects.filter(status='CANCELLED').count(), 2)
        self.assertEqual(ImportReceipt.objects.filter(status='APPROVED').count(), 6)
        self.assertEqual(ImportReceipt.objects.filter(status='PENDING').count(), 5)
        self.assertEqual(ImportReceipt.objects.filter(status='REJECTED').count(), 4)
        self.assertEqual(ExportReceipt.objects.filter(status='PENDING').count(), 7)
        self.assertEqual(ExportReceipt.objects.filter(status='APPROVED').count(), 6)
        self.assertEqual(ExportReceipt.objects.filter(status='REJECTED').count(), 2)
        self.assertGreaterEqual(ImportReceipt.objects.filter(created_by__role='ADMIN').count(), 3)
        self.assertGreaterEqual(ImportReceipt.objects.filter(created_by__role='KHO').count(), 5)
        self.assertGreaterEqual(ImportReceipt.objects.exclude(reviewed_by=None).filter(reviewed_by__role='ADMIN').count(), 3)
        self.assertGreaterEqual(ImportReceipt.objects.exclude(reviewed_by=None).filter(reviewed_by__role='KE_TOAN').count(), 5)
        self.assertGreaterEqual(ExportReceipt.objects.filter(created_by__role='ADMIN').count(), 3)
        self.assertGreaterEqual(ExportReceipt.objects.filter(created_by__role='KHO').count(), 5)
        self.assertGreaterEqual(ExportReceipt.objects.exclude(reviewed_by=None).filter(reviewed_by__role='ADMIN').count(), 2)
        self.assertGreaterEqual(ExportReceipt.objects.exclude(reviewed_by=None).filter(reviewed_by__role='KE_TOAN').count(), 5)

