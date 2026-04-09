"""
apps/product/test_validators.py
Unit Test cho các validator trong module Product
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from .validators import (
    ProductValidator,
    CategoryValidator,
    ProductUnitValidator,
    validate_product_name_unique,
    validate_category_name_unique,
)
from .models import Product, Category, ProductUnit


class TestProductValidator(TestCase):
    """Test ProductValidator"""

    def setUp(self):
        self.validator = ProductValidator()
        self.category = Category.objects.create(name='Test Category')

    def test_validate_product_name_valid(self):
        """Test tên sản phẩm hợp lệ"""
        name = 'Xi măng Hà Tiên PCB40'
        result = ProductValidator.validate_product_name(name)
        self.assertEqual(result.strip(), name.strip())

    def test_validate_product_name_empty(self):
        """Test tên sản phẩm rỗng"""
        with self.assertRaises(ValidationError) as context:
            ProductValidator.validate_product_name('')
        self.assertIn('không được để trống', str(context.exception))

    def test_validate_product_name_too_short(self):
        """Test tên sản phẩm quá ngắn"""
        with self.assertRaises(ValidationError) as context:
            ProductValidator.validate_product_name('Xi')
        self.assertIn('ít nhất 3 ký tự', str(context.exception))

    def test_validate_product_name_too_long(self):
        """Test tên sản phẩm quá dài"""
        name = 'a' * 256
        with self.assertRaises(ValidationError) as context:
            ProductValidator.validate_product_name(name)
        self.assertIn('vượt quá 255 ký tự', str(context.exception))

    def test_validate_product_name_special_chars(self):
        """Test tên sản phẩm có ký tự đặc biệt"""
        with self.assertRaises(ValidationError) as context:
            ProductValidator.validate_product_name('Xi <măng>')
        self.assertIn('ký tự không hợp lệ', str(context.exception))

    def test_validate_base_price_valid(self):
        """Test giá cơ bản hợp lệ"""
        price = Decimal('95000.50')
        result = ProductValidator.validate_base_price(price)
        self.assertEqual(result, price)

    def test_validate_base_price_zero(self):
        """Test giá cơ bản bằng 0"""
        with self.assertRaises(ValidationError) as context:
            ProductValidator.validate_base_price(0)
        self.assertIn('lớn hơn 0', str(context.exception))

    def test_validate_base_price_negative(self):
        """Test giá cơ bản âm"""
        with self.assertRaises(ValidationError) as context:
            ProductValidator.validate_base_price(-50000)
        self.assertIn('không được là số âm', str(context.exception))

    def test_validate_base_price_invalid_type(self):
        """Test giá cơ bản không phải số"""
        with self.assertRaises(ValidationError) as context:
            ProductValidator.validate_base_price('abc')
        self.assertIn('phải là một số', str(context.exception))

    def test_validate_base_unit_valid(self):
        """Test đơn vị cơ bản hợp lệ"""
        unit = 'Bao'
        result = ProductValidator.validate_base_unit(unit)
        self.assertEqual(result.strip(), unit.strip())

    def test_validate_base_unit_empty(self):
        """Test đơn vị cơ bản rỗng"""
        with self.assertRaises(ValidationError) as context:
            ProductValidator.validate_base_unit('')
        self.assertIn('không được để trống', str(context.exception))

    def test_validate_base_unit_too_long(self):
        """Test đơn vị cơ bản quá dài"""
        unit = 'a' * 51
        with self.assertRaises(ValidationError) as context:
            ProductValidator.validate_base_unit(unit)
        self.assertIn('vượt quá 50 ký tự', str(context.exception))


class TestCategoryValidator(TestCase):
    """Test CategoryValidator"""

    def test_validate_category_name_valid(self):
        """Test tên danh mục hợp lệ"""
        name = 'Sắt thép'
        result = CategoryValidator.validate_category_name(name)
        self.assertEqual(result.strip(), name.strip())

    def test_validate_category_name_empty(self):
        """Test tên danh mục rỗng"""
        with self.assertRaises(ValidationError) as context:
            CategoryValidator.validate_category_name('')
        self.assertIn('không được để trống', str(context.exception))

    def test_validate_category_name_too_short(self):
        """Test tên danh mục quá ngắn"""
        with self.assertRaises(ValidationError) as context:
            CategoryValidator.validate_category_name('X')
        self.assertIn('ít nhất 2 ký tự', str(context.exception))

    def test_validate_category_name_special_chars(self):
        """Test tên danh mục có ký tự đặc biệt"""
        with self.assertRaises(ValidationError) as context:
            CategoryValidator.validate_category_name('Sắt <thép>')
        self.assertIn('ký tự không hợp lệ', str(context.exception))


class TestProductUnitValidator(TestCase):
    """Test ProductUnitValidator"""

    def test_validate_unit_name_valid(self):
        """Test tên đơn vị hợp lệ"""
        name = 'Tấn'
        result = ProductUnitValidator.validate_unit_name(name)
        self.assertEqual(result.strip(), name.strip())

    def test_validate_unit_name_empty(self):
        """Test tên đơn vị rỗng"""
        with self.assertRaises(ValidationError) as context:
            ProductUnitValidator.validate_unit_name('')
        self.assertIn('không được để trống', str(context.exception))

    def test_validate_conversion_rate_valid(self):
        """Test tỷ lệ quy đổi hợp lệ"""
        rate = Decimal('1000')
        result = ProductUnitValidator.validate_conversion_rate(rate)
        self.assertEqual(result, rate)

    def test_validate_conversion_rate_zero(self):
        """Test tỷ lệ quy đổi bằng 0"""
        with self.assertRaises(ValidationError) as context:
            ProductUnitValidator.validate_conversion_rate(0)
        self.assertIn('lớn hơn 0', str(context.exception))

    def test_validate_conversion_rate_negative(self):
        """Test tỷ lệ quy đổi âm"""
        with self.assertRaises(ValidationError) as context:
            ProductUnitValidator.validate_conversion_rate(-100)
        self.assertIn('lớn hơn 0', str(context.exception))

    def test_validate_conversion_rate_invalid_type(self):
        """Test tỷ lệ quy đổi không phải số"""
        with self.assertRaises(ValidationError) as context:
            ProductUnitValidator.validate_conversion_rate('abc')
        self.assertIn('phải là một số', str(context.exception))


class TestValidateProductNameUnique(TestCase):
    """Test validate_product_name_unique"""

    def setUp(self):
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Xi măng Hà Tiên',
            category=self.category,
            base_price=Decimal('95000'),
            base_unit='Bao'
        )

    def test_unique_name_valid(self):
        """Test tên sản phẩm không trùng lặp"""
        # Không raise exception
        validate_product_name_unique('Sắt Phi 10', exclude_id=self.product.id)

    def test_unique_name_duplicate(self):
        """Test tên sản phẩm trùng lặp"""
        with self.assertRaises(ValidationError) as context:
            validate_product_name_unique('Xi măng Hà Tiên')
        self.assertIn('đã tồn tại', str(context.exception))

    def test_unique_name_case_insensitive(self):
        """Test kiểm tra không phân biệt hoa thường"""
        with self.assertRaises(ValidationError) as context:
            validate_product_name_unique('xi măng hà tiên')
        self.assertIn('đã tồn tại', str(context.exception))

    def test_unique_name_exclude_self(self):
        """Test không báo lỗi khi chỉnh sửa chính sản phẩm"""
        # Không raise exception - loại trừ chính nó
        validate_product_name_unique('Xi măng Hà Tiên', exclude_id=self.product.id)


class TestValidateCategoryNameUnique(TestCase):
    """Test validate_category_name_unique"""

    def setUp(self):
        self.category = Category.objects.create(name='Gạch Xây Dựng')

    def test_unique_name_valid(self):
        """Test tên danh mục không trùng lặp"""
        validate_category_name_unique('Sắt Thép')

    def test_unique_name_duplicate(self):
        """Test tên danh mục trùng lặp"""
        with self.assertRaises(ValidationError) as context:
            validate_category_name_unique('Gạch Xây Dựng')
        self.assertIn('đã tồn tại', str(context.exception))

    def test_unique_name_case_insensitive(self):
        """Test kiểm tra không phân biệt hoa thường"""
        with self.assertRaises(ValidationError) as context:
            validate_category_name_unique('gạch xây dựng')
        self.assertIn('đã tồn tại', str(context.exception))