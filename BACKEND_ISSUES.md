# Backend & Docker Configuration Issues Report

## Summary
The current Docker configuration prevents successful orchestration of the backend services (Django, Celery, Redis, Postgres). Additionally, CORS settings need to be updated to support the frontend development environment.

## Issues to Fix

### 1. Docker Compose Network & Connectivity
**Issue:**  
The Celery worker fails to connect to Redis with the error: `Error -5 connecting to redis:6379. No address associated with hostname`.
**Cause:**  
Services are not sharing a defined Docker bridge network, or service discovery is failing due to race conditions.
**Required Fix in `docker-compose.yml`:**
- Define a custom bridge network (e.g., `premium_store_net`) and assign all services (`db`, `redis`, `backend`, `celery`, `frontend`) to it.
- Implement `healthcheck` for Redis.
- Update `depends_on` for `backend` and `celery` to wait for valid health conditions of `db` and `redis`.

### 2. CORS Settings (Frontend Access)
**Issue:**  
The frontend running on port 3006 is blocked by CORS.
**Required Fix in `premium_store_backend/config/settings.py`:**
- Add `http://localhost:3006` and `http://127.0.0.1:3006` to `CORS_ALLOWED_ORIGINS`.

### 3. Frontend Service Definition (For Context)
The frontend is now configured to run on port `3006` to avoid conflicts.
Please ensure the `docker-compose.yml` includes a `frontend` service definition similar to:
```yaml
  frontend:
    build:
      context: ./premium_store_frontend
    ports:
      - "3006:3005"
    depends_on:
      - backend
    networks:
      - premium_store_net
```
