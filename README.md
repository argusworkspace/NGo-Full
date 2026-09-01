# NGO Survey Management System — Monorepo

Combines the two previously separate repositories into one:

```
NGo-Full/
├── frontend/   Next.js 15 (App Router) — from argusworkspace/ngo, branch `dev`
└── backend/    FastAPI + SQLAlchemy (async) + Alembic — from argusworkspace/ngo-backend, branch `feature/database`
```

Each subfolder is a snapshot of that project's tracked files (`git archive`) at the time this monorepo was created — commit history was not carried over. Each keeps its own dependency manifest, `.gitignore` rules (mirrored at the repo root), and README with setup instructions specific to that half of the stack.

## Getting started

**Backend** (`backend/`):
```bash
cd backend
python -m venv .venv && .venv/Scripts/activate   # Windows; source .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
cp .env.example .env   # fill in DATABASE_URL (Neon) and APP_SECRET_KEY
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --port 8000
```

**Frontend** (`frontend/`):
```bash
cd frontend
npm install
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_URL to the backend above
npm run dev
```

See `backend/README.md` and `frontend/README.md` for full details (API reference, JWT/role model, question types, testing).
