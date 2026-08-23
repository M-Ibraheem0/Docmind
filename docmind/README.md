# DocMind — AI Document Q&A Backend

Finding a specific answer across 50 documents took 45 minutes manually. DocMind returns a cited answer in under 10 seconds.

## Concepts Implemented

| #   | Concept         | Location                                          |
| --- | --------------- | ------------------------------------------------- |
| 1   | API endpoints   | app/api/v1/                                       |
| 2   | Database        | app/models/, PostgreSQL + pgvector                |
| 3   | Authentication  | app/api/v1/auth.py, JWT                           |
| 4   | Background jobs | app/background/tasks.py                           |
| 5   | Reporting PDF   | app/api/v1/reports.py, app/services/pdf_report.py |
| 6   | Caching         | app/services/cache.py, Redis                      |
| 7   | LLM integration | app/services/rag.py, LangChain + LangSmith        |

## Stack

- FastAPI, PostgreSQL + pgvector, Redis, LangChain, OpenAI, WeasyPrint

## Run

```bash
cp .env.example .env
# fill in your keys in .env

docker compose up -d
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Go to http://localhost:8000/docs

## Demo Path

1. POST /api/v1/auth/register — create account
2. POST /api/v1/auth/login — get token, click Authorize in swagger
3. POST /api/v1/documents/upload — upload a PDF
4. GET /api/v1/documents/{id} — wait for status: ready
5. POST /api/v1/conversations/ask — ask a question, get cited answer
6. Ask same question again — see cached: true, instant response
7. POST /api/v1/reports/export — download answer as PDF
