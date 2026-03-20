# RoboYard Control Backend

FastAPI, simulator, Celery, and data services for the RoboYard Control operations platform.

## Commands

```bash
cp .env.example .env
python3 -m pip install -e '.[dev]'
uvicorn app.main:app --reload --port 8000
python3 -m pytest tests -q
```

## Notes

- The backend supports PostgreSQL in normal runtime and SQLite in tests.
- Demo seeding is deterministic and enabled by default for local portfolio walkthroughs.
- Background jobs are wired through Celery + Redis even though the simulator loop runs inside the FastAPI lifecycle for realtime demo streaming.
