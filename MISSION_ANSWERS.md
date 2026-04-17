# Day 12 Lab - Mission Answers

> **Student:** Lê Thị Phương
> **Student ID:** 2A202600107 
> **Date:** 2026-04-17

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found

1. API key hardcode (sk-hardcoded-fake-key...) 

   -> Nếu push lên GitHub, key/password bị lộ ngay lập tức. Attacker có thể dùng key của bạn để gọi API, gây bill khổng lồ.
3. Database URL hardcode 

   -> Lộ credentials  
5. Print thay vì proper logging + log ra secret:

   ->  Dùng `print()` thay vì structured logging. Nghiêm trọng hơn là log ra API key — bất kỳ ai xem log đều thấy secret.

7. Không có /health endpoint 
   -> Khi deploy lên cloud (Railway, Render, K8s), platform không có cách nào biết agent có còn sống không. Nếu agent crash, platform không tự restart được.

8. Port cứng (localhost:8000) 
   ```python
   host="localhost",  # chỉ chạy trên local
   port=8000,         # cứng port
   ```

    -> `localhost` chỉ cho phép kết nối từ chính máy đó, container bên ngoài không truy cập được. Port cứng xung đột với port mà cloud platform inject qua `PORT` env var.

10. Debug reload 

    -> `reload=True` chỉ dùng khi develop. Trong production, nó gây restart không cần thiết, tiêu tốn resource và có thể gây mất request.

12. Không graceful shutdown 

    -> Khi server nhận SIGTERM (tín hiệu dừng), nó tắt đột ngột. Request đang xử lý bị ngắt (BrokenPipeError), dữ liệu có thể chưa được lưu, gây trải nghiệm tồi cho user.

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config  | Hardcode trong code | Env vars + config.py | Không lộ secrets, dễ deploy |
| Logging | print() | Structured JSON logging | Dễ parse trong log aggregators | 
| Health check |  Không có | GET /health + GET /ready | Cloud biết khi nào restart |
| Shutdown | Đột ngột (BrokenPipeError) | Signal handler (SIGTERM) | Requests hoàn thành gracefully | 
| Host:Port | localhost:8000 cứng | 0.0.0.0:{PORT} từ env | Chạy được trong container + cloud | 
| CORS |  Không có | CORSMiddleware | Bảo vệ API từ cross-origin requests | 
| Debug mode | Luôn ON (reload=True) | Kiểm soát bằng DEBUG env var | Hiệu suất + security |
...

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: [Your answer]
2. Working directory: [Your answer]
...

# Giải Thích Dockerfile Cơ Bản

| Câu Hỏi | Trả Lời | Giải Thích |
| :--- | :--- | :--- |
| **Base image là gì?** | `python:3.11` | Sử dụng bản phân phối Python đầy đủ (Full Distro), dung lượng ~1.5 GB. |
| **Working directory?** | `/app` | Thư mục làm việc bên trong container, nơi code sẽ được thực thi. |
| **Tại sao COPY requirements.txt trước?** | **Docker layer cache** | Giúp tối ưu hóa build image. Nếu code thay đổi nhưng thư viện giữ nguyên, lệnh `pip install` sẽ được lấy từ cache, giúp build cực nhanh. |
| **CMD vs ENTRYPOINT khác nhau?** | **CMD** = default command. | `CMD` có thể bị ghi đè (override) khi chạy lệnh `docker run`, trong khi `ENTRYPOINT` thường được dùng cho các lệnh cố định. |

---


### Exercise 2.3: Image size comparison
- Develop: 1177.6 MB
- Production: 160 MB
- Difference: 86.41 %


Đọc `02-docker/production/Dockerfile`:

- **Stage 1 (builder):** Dùng `python:3.11-slim`, cài gcc + build tools, pip install dependencies vào `--user` path (`/root/.local`).
- **Stage 2 (runtime):** Dùng `python:3.11-slim` sạch, chỉ COPY `/root/.local` từ builder. Không có gcc, build tools → image nhỏ hơn nhiều.
- **Tại sao image nhỏ hơn?** Vì stage 2 không chứa build tools (gcc, libpq-dev), pip cache, apt cache. Chỉ giữ runtime dependencies.

| Image | Estimated Size | Lý do |
|-------|---------------|-------|
| `agent-develop` (single-stage, python:3.11) | 1.5 GB | Full Python + all build tools |
| `agent-production` (multi-stage, python:3.11-slim) | ~160 MB | Chỉ runtime, không build tools |


### Exercise 2.4: Docker Compose architecture

Đọc `02-docker/production/docker-compose.yml`:

```
┌──────────────┐
│    Client    │
└──────┬───────┘
       │ :80/:443
       ▼
┌──────────────┐
│    Nginx     │  ← Reverse proxy + load balancer + rate limiting
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    Agent     │  ← FastAPI app (có thể scale nhiều replicas)
└──────┬───────┘
       │
  ┌────┴────┐
  ▼         ▼
┌──────┐ ┌────────┐
│Redis │ │ Qdrant │  ← Cache/rate limiting  +  Vector DB cho RAG
└──────┘ └────────┘
```

**Services được start:**
1. **agent** — FastAPI AI agent (phụ thuộc Redis + Qdrant healthy)
2. **redis** — Cache cho session và rate limiting
3. **qdrant** — Vector database cho RAG
4. **nginx** — Reverse proxy, load balancer, rate limiting (10r/s)

**Communication:**
- Client → Nginx (port 80/443)
- Nginx → Agent (port 8000, internal network)
- Agent → Redis (port 6379, internal network)
- Agent → Qdrant (port 6333, internal network)
- Tất cả qua Docker network `internal` (bridge driver)


## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://agent-production-7c44.up.railway.app/docs
- Screenshot: ![alt text](Screenshot%202026-04-17%20162422.png)


## Part 4: API Security

### Exercise 4.1-4.3: Test results

4.1. 1. Chạy thử API Key (Exercise 4.1)

![alt text](screenshots/image-1.png)
![alt text](screenshots/image-2.png)

Thử không có Key:
{"detail":"Missing API key. Include header: X-API-Key: <your-key>"}

Thử có key:
{"question":"Hello","answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé."}

4.2. Chạy thử JWT & Rate Limit (Exercise 4.2 - 4.3)

```
curl -X POST http://localhost:8000/auth/token -H "Content-Type: application/json" -d "{\"username\": \"student\", \"password\": \"demo123\"}"
```
result:
{"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHVkZW50Iiwicm9sZSI6InVzZXIiLCJpYXQiOjE3NzY0MzEzNDQsImV4cCI6MTc3NjQzNDk0NH0.dGuy49ka27bsW_3h-JsIDLO-Oademun2oaVGQJPuFwY","token_type":"bearer","expires_in_minutes":60,"hint":"Include in header: Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."}

```
curl -X POST http://localhost:8000/ask ^
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHVkZW50Iiwicm9sZSI6InVzZXIiLCJpYXQiOjE3NzY0MzEzNDQsImV4cCI6MTc3NjQzNDk0NH0.dGuy49ka27bsW_3h-JsIDLO-Oademun2oaVGQJPuFwY" ^
  -H "Content-Type: application/json" ^
  -d "{\"question\": \"Explain JWT\"}"

```
result:
{"question":"Explain JWT","answer":"Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.","usage":{"requests_remaining":9,"budget_remaining_usd":1.9e-05}}



for /L %i in (1,1,20) do curl -X POST http://localhost:8000/ask -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHVkZW50Iiwicm9sZSI6InVzZXIiLCJpYXQiOjE3NzY0MzEzNDQsImV4cCI6MTc3NjQzNDk0NH0.dGuy49ka27bsW_3h-JsIDLO-Oademun2oaVGQJPuFwY" -H "Content-Type: application/json" -d "{\"question\": \"Test %i\"}"

Result: {"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":54}}

### Exercise 4.4: Cost guard implementation

- Lưu trữ: Sử dụng Redis để lưu trữ thông tin chi phí vì nó hỗ trợ thao tác toán học nguyên tử (incrbyfloat) và có thể truy cập từ nhiều server khác nhau.
- Cấu trúc Key: Đặt tên Key kèm theo user_id và tháng/năm (Ví dụ: budget:user1:2026-04). Việc này giúp hệ thống tự động có "ngân sách mới" khi bước sang tháng tiếp theo mà không cần lệnh xóa data cũ.
- Cơ chế chặn: Tính toán chi phí ước tính dựa trên số lượng Token của câu hỏi và câu trả lời. Nếu tổng chi phí trong tháng vượt quá $10, hệ thống sẽ trả về lỗi 402 Payment Required, ngăn chặn việc gọi LLM tiếp để bảo vệ tài chính.

![alt text](screenshots/test_cost_guard.PNG)


## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes

### Exercise 5.1: Health Checks

Đọc `05-scaling-reliability/develop/app.py`:

```python
@app.get("/health")
def health():
    """Liveness probe — container còn sống không?"""
    # Check uptime, memory usage (via psutil)
    # Return: {"status": "ok"/"degraded", "uptime_seconds": ..., "checks": {...}}
    return {"status": "ok", ...}

@app.get("/ready")
def ready():
    """Readiness probe — sẵn sàng nhận traffic không?"""
    if not _is_ready:
        raise HTTPException(503, "Agent not ready")
    return {"ready": True, "in_flight_requests": _in_flight_requests}
```

**Sự khác biệt:**
- `/health` (Liveness): "App có còn chạy không?" → non-200 = platform restart container
- `/ready` (Readiness): "App có sẵn sàng nhận request không?" → non-200 = load balancer ngừng route traffic vào instance này (nhưng không restart)

### Exercise 5.2: Graceful Shutdown

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load model, connect DB
    _is_ready = True
    yield
    # Shutdown:
    _is_ready = False  # 1. Ngừng nhận request mới (readiness = 503)
    while _in_flight_requests > 0:  # 2. Chờ request đang xử lý
        time.sleep(1)
    # 3. Close connections
    # 4. Exit
```

Kết hợp với `signal.signal(signal.SIGTERM, handle_sigterm)` và `timeout_graceful_shutdown=30` trong uvicorn.

### Exercise 5.3: Stateless Design

**Anti-pattern (stateful):**
```python
# State trong memory
conversation_history = {}  # Mất khi restart, không share giữa instances
```

**Correct (stateless):**
```python
# State trong Redis
def save_session(session_id, data):
    _redis.setex(f"session:{session_id}", ttl, json.dumps(data))

def load_session(session_id):
    return json.loads(_redis.get(f"session:{session_id}"))
```

**Tại sao quan trọng?** Khi scale ra 3 instances:
- Stateful: User A request 1 → Instance 1 (lưu history). Request 2 → Instance 2 (không có history!) → Bug!
- Stateless + Redis: Bất kỳ instance nào cũng đọc được session từ Redis.

### Exercise 5.4: Load Balancing

Đọc `05-scaling-reliability/production/docker-compose.yml` + `nginx.conf`:

- Nginx dùng Docker DNS resolver (`127.0.0.11`) để tìm agent containers
- `upstream agent_cluster { server agent:8000; }` → Docker round-robin giữa instances
- `proxy_next_upstream error timeout http_503` → nếu 1 instance fail, chuyển sang instance khác
- Scale: `docker compose up --scale agent=3` → 3 instances

### Exercise 5.5: Test Stateless

`test_stateless.py` chứng minh:
1. Tạo 1 session, gửi 5 câu hỏi liên tiếp
2. Mỗi request có thể được serve bởi instance khác (xem `served_by`)
3. Conversation history vẫn đầy đủ vì lưu trong Redis
4. Output: "Session history preserved across all instances via Redis!"

---

Kết quả thử nghiệm (Test Results)

{"session_id":"123","question":"Hello","answer":"Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.","turn":2,"served_by":"instance-c3cd01","storage":"redis"}

![alt text](screenshots/running.png)

## Part 6: Final Project

### Implementation Summary

Project `06-lab-complete/` kết hợp tất cả concepts:

| Feature | File | Status |
|---------|------|--------|
| Config từ env vars | `app/config.py` | ✅ |
| Structured JSON logging | `app/main.py` | ✅ |
| API Key authentication | `app/main.py` → `verify_api_key()` | ✅ |
| Rate limiting (20 req/min) | `app/main.py` → `check_rate_limit()` | ✅ |
| Cost guard ($5/day) | `app/main.py` → `check_and_record_cost()` | ✅ |
| Health check `/health` | `app/main.py` | ✅ |
| Readiness `/ready` | `app/main.py` | ✅ |
| Graceful shutdown (SIGTERM) | `app/main.py` → `_handle_signal()` | ✅ |
| Input validation (Pydantic) | `AskRequest` model | ✅ |
| Security headers | Middleware | ✅ |
| CORS | CORSMiddleware | ✅ |
| Multi-stage Dockerfile | `Dockerfile` | ✅ |
| Non-root user | `Dockerfile` → `USER agent` | ✅ |
| Docker Compose + Redis | `docker-compose.yml` | ✅ |
| Railway config | `railway.toml` | ✅ |
| Render config | `render.yaml` | ✅ |
| `.dockerignore` | `.dockerignore` | ✅ |
| `.env.example` | `.env.example` | ✅ |
