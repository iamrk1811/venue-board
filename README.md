# Venue Board

A real-time hospitality operations dashboard. Venues (pubs, restaurants, function spaces) send POS transactions to the API, the dashboard updates live via WebSocket and raises anomaly alerts when sales drop or void/refund rates spike.

---

| Layer | Tech |
|---|---|
| API + WebSocket server | Django, Django Channels, Uvicorn |
| Task queue | Celery, Redis |
| Database | PostgreSQL |
| Cache | Redis |
| Frontend | React, Redux Toolkit, Recharts, Tailwind CSS, Vite |
| Auth | JWT |

---

## Running with Docker (recommended)

```bash
# 1. Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 2. Start all services
docker compose up --build

# 3. In a separate terminal seed venues and a superuser
docker compose exec backend python manage.py seed_venues
docker compose exec backend python manage.py createsuperuser
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| API | http://localhost:8000/api/ |
| Swagger UI | http://localhost:8000/api/docs/ |
| Django admin | http://localhost:8000/admin/ |


## Running locally (without Docker)

**Prerequisites:** Python 3.12, Node 20+, a running PostgreSQL instance, a running Redis instance.

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# Set env vars (examples are present on .env.example)
python manage.py migrate
python manage.py seed_venues
python manage.py createsuperuser

# Celery worker
celery -A venueboard worker -Q metrics --concurrency=4 -l info

# Backend server
uvicorn venueboard.asgi:application --host 0.0.0.0 --port 8000 --reload


```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Running tests

```bash
cd backend
source venv/bin/activate
pytest
```

---

## Transactions Simulator for localhost

```bash
python manage.py simulate_transactions --rate 3
```

`--rate 3` sends 3 transactions per second across all seeded venues, mix of sales / voids / refunds.

---

## Key decisions

### Async write with Celery and WebSocket push

`POST /api/transactions/` writes the transaction synchronously (for durability), then immediately start `process_transaction` Celery task. The task runs `MetricsService`, `AnomalyService`, updates the Redis cache, and push the new summary to dashboard. This keeps API response times low and decouples metric computation from the request lifecycle.

### Accumulative cache instead of full rebuilds

`core/cache.py` maintains a single Redis key (`dashboard:summary:<date>`) that holds the complete dashboard payload. On each transaction the worker accumulates updates. A full DB rebuild (`build_summary`) only happens on a cache miss or when a brand new venue appears for the first time that day. TTL is 15 minutes as a safety net so stale data never persists through a worker crash.


### Anomaly detection rules

Three detectors run after every transaction for the affected venue. All three require at least 5 transactions in both the current and previous hour before firing, to avoid noise on low volume. Alerts automatically resolve when the metric recovers.

- **Sales drop** compares current-hour total sales against the previous hour. Raises `warning` at ≥40% drop, `critical` at ≥70% (configurable via `SALES_DROP_PERCENT` and `SALES_DROP_CRITICAL_PERCENT`).
- **Void spike** compares the current hour's void rate (voids ÷ transactions) against the previous hour's void rate. Raises `warning` at ≥50% increase, `critical` at ≥70% increase (configurable via `VOID_SPIKE_PERCENT` and `VOID_SPIKE_CRITICAL_PERCENT`). No alert fires if the previous hour had a zero void rate.
- **Refund spike** applies the same percentage logic to refund rates. Raises `warning` at ≥50% increase, `critical` at ≥70% increase (configurable via `REFUND_SPIKE_PERCENT` and `REFUND_SPIKE_CRITICAL_PERCENT`).

### Single shared WebSocket group

All authenticated clients join the `dashboard` channel group. The worker broadcasts to the group, every connected ops member receives every update.

---

## What I'd improve with more time

**Venue scoped WebSocket group** currently every client receives updates for every venue. With many venues and many connected clients, switching to per venue groups (`dashboard:venue:<id>`) would let the frontend subscribe only to the venues it's displaying, reducing unnecessary renders.

**Idempotent transaction ingestion** the `POST /api/transactions/` endpoint does not deduplicate. A retry from a POS terminal that timed out would create a duplicate transaction and double-count metrics. Adding a client supplied idempotency key (UUID) with a short Redis TTL guard would fix this.

**Pagination on transaction history** there is no endpoint to browse historical transactions. Useful for audit/drill-down from the dashboard.
