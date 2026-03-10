# 1. Chọn môi trường Python gốc
FROM python:3.12

# 2. Ngăn Python tạo file .pyc và ép log xuất thẳng ra terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Cài đặt các thư viện hệ thống cần thiết cho mysqlclient
RUN apt-get update \
    && apt-get install -y default-libmysqlclient-dev build-essential pkg-config \
    && rm -rf /var/lib/apt/lists/* # Xóa cache apt để image nhẹ hơn

# 4. Tạo thư mục làm việc
WORKDIR /app

# 5. Copy file requirements và cài đặt thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy toàn bộ mã nguồn vào container
COPY . .