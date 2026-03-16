import logging
from django.http import JsonResponse
from apps.core.exceptions import LoiTuyChon

logger = logging.getLogger(__name__)

class XuLyLoiMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        # Log lỗi ra console để dev theo dõi
        logger.error(f"❌ Lỗi: {exception}", exc_info=True)

        # Nếu là lỗi tùy chọn của chúng ta
        if isinstance(exception, LoiTuyChon):
            return JsonResponse({
                'thanhCong': False,
                'maLoi': exception.ma_loi,
                'thongBao': exception.thong_bao,
                'chiTiet': exception.chi_tiet
            }, status=exception.ma_http)

        # Lỗi không mong đợi (ví dụ lỗi code, lỗi DB)
        return JsonResponse({
            'thanhCong': False,
            'maLoi': 'INTERNAL_ERROR',
            'thongBao': 'Đã xảy ra lỗi, vui lòng thử lại sau'
        }, status=500)