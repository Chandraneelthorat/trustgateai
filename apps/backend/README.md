# TrustGateAI backend

FastAPI application, SQLAlchemy models, Celery worker, and LangGraph agent stubs.

## Local development

```bash
cd apps/backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[metrics]"   # or pip install -e . for core only
cp ../../.env.example ../../.env
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Start Celery (separate terminal):

```bash
celery -A app.worker:celery_app worker --loglevel=INFO
```

With `SKIP_CELERY_SYNC=1`, `POST /evaluations` runs the pipeline synchronously in the API process (no worker required).

## Tests

```bash
pip install -e ".[test]"
pytest
```

The suite runs against an isolated SQLite database (models are cross-dialect), so no
running Postgres or Redis is required. RAGAS/DeepEval are optional; their degraded paths
are covered too.
