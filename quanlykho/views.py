from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError

def health_check(request):
    """
    Endpoint kiểm tra sức khỏe của API và kết nối với Cơ sở dữ liệu.
    """
    health_status = {
        "api": "ok",
        "database": "ok"
    }
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
