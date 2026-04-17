# Deployment Information

> **Student:** Lê Thị Phương 
> **Student ID:** 2A202600107
> **Date:** 2026-04-17

---


## Public URL
https://lab11-production-3c63.up.railway.app/

## Platform
Railway / Render / Cloud Run

## Local Development

### Prerequisites
```bash
python 3.11+
docker & docker compose
redis (optional — app fallback to in-memory)
```

### Run Locally (without Docker)
```bash
cd 06-lab-complete
pip install -r requirements.txt
python -m app.main
```

### Run with Docker Compose
```bash
cd 06-lab-complete
docker compose up --build
```

## Test Commands

### Health Check
```bash
curl https://lab11-production-3c63.up.railway.app/health
# Expected: {"status": "ok"}
#{"status":"ok","uptime_seconds":18153.1,"platform":"Railway","timestamp":"2026-04-17T15:02:58.708975+00:00"}
```

### API Test (with authentication)
```bash
curl -X POST https://lab11-production-3c63.up.railway.app/ask ^
  -H "X-API-Key: YOUR_KEY" ^
  -H "Content-Type: application/json" ^
  -d "{\"question\": \"Hello Railway!\"}"
# {"question":"Hello Railway!","answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé.","platform":"Railway"}
```

### View Metrics (protected)
```bash
curl https://lab11-production-3c63.up.railway.app/metrics \
  -H "X-API-Key: YOUR_KEY"
```

## Environment Variables Set
| Variable | Description | Required |
|----------|-------------|----------|
| `PORT` | Server port (default: 8000) | Auto-injected by Railway |
| `ENVIRONMENT` | `development` / `production` | Yes |
| `AGENT_API_KEY` | API key for authentication | Yes (production) |
| `JWT_SECRET` | JWT signing secret | Yes (production) |
| `REDIS_URL` | Redis connection URL | Optional |
| `OPENAI_API_KEY` | OpenAI API key (empty = mock LLM) | Optional |
| `RATE_LIMIT_PER_MINUTE` | Max requests per minute (default: 20) | No |
| `DAILY_BUDGET_USD` | Daily cost budget (default: 5.0) | No |
| `LOG_LEVEL` | Logging level | No |
| `ALLOWED_ORIGINS` | CORS origins (comma-separated) | No |

## Screenshots
- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Test results](screenshots/test.png)


## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────────┐
│  Agent (FastAPI) │  ← API Key Auth + Rate Limit + Cost Guard
└──────┬──────────┘
       │
       ▼
┌──────────────┐
│    Redis     │  ← Session cache (optional, fallback to in-memory)
└──────────────┘
```
##  Pre-Submission Checklist

- [ ] Repository is public (or instructor has access)
- [ ] `MISSION_ANSWERS.md` completed with all exercises
- [ ] `DEPLOYMENT.md` has working public URL
- [ ] All source code in `app/` directory
- [ ] `README.md` has clear setup instructions
- [ ] No `.env` file committed (only `.env.example`)
- [ ] No hardcoded secrets in code
- [ ] Public URL is accessible and working
- [ ] Screenshots included in `screenshots/` folder
- [ ] Repository has clear commit history

---

##  Self-Test

Before submitting, verify your deployment:

```bash
# 1. Health check
curl https://your-app.railway.app/health

# 2. Authentication required
curl https://your-app.railway.app/ask
# Should return 401

# 3. With API key works
curl -H "X-API-Key: YOUR_KEY" https://your-app.railway.app/ask \
  -X POST -d '{"user_id":"test","question":"Hello"}'
# Should return 200

# 4. Rate limiting
for i in {1..15}; do 
  curl -H "X-API-Key: YOUR_KEY" https://your-app.railway.app/ask \
    -X POST -d '{"user_id":"test","question":"test"}'; 
done
# Should eventually return 429
```

---

##  Submission

**Submit your GitHub repository URL:**

```
https://github.com/your-username/day12-agent-deployment
```

**Deadline:** 17/4/2026

---

##  Quick Tips

1.  Test your public URL from a different device
2.  Make sure repository is public or instructor has access
3.  Include screenshots of working deployment
4.  Write clear commit messages
5.  Test all commands in DEPLOYMENT.md work
6.  No secrets in code or commit history

---

##  Need Help?

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review [CODE_LAB.md](CODE_LAB.md)
- Ask in office hours
- Post in discussion forum

---

**Good luck! **
