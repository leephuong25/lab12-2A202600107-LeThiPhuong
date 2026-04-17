FROM python:3.11-slim

WORKDIR /app

# Cài đặt dependencies
RUN pip install --no-cache-dir fastapi uvicorn redis pydantic

# Copy code của Part 5 vào container
COPY app.py .
COPY utils ./utils

# Thiết lập môi trường
ENV PYTHONPATH=/app
EXPOSE 8000

# Chạy ứng dụng (file app.py)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
