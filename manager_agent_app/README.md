# Manager Agent (Side-loaded App)

This is an **independent Flask application** for manager/sub-agent orchestration, intentionally separated from the existing app in this repository.

## What it does
- Accepts a high-level project objective.
- Creates role-based sub-agents (e.g., Data Engineer, Scrum Master, Data Scientist, Software Engineer).
- Generates and assigns tasks.
- Monitors progress on a configurable cadence.
- Detects and resolves blocked tasks.
- Exposes live state through an API + dashboard.

## Project structure
- `manager_agent_app/app.py` - backend + APIs + monitoring loop
- `manager_agent_app/templates/manager_dashboard.html` - dashboard
- `manager_agent_app/.env.example` - environment variable template
- `manager_agent_app/requirements.txt` - dependencies

## Quickstart
```bash
cd manager_agent_app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

Open: `http://localhost:5050`

## Configuration
Set these in `manager_agent_app/.env`:
- `PORT` (default `5050`)
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_DEPLOYMENT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_API_VERSION`

If Azure variables are missing, the app still runs with local in-memory planning logic.

## API endpoints
- `POST /api/objective` - set objective and optional roles
- `POST /api/config` - set `poll_interval_seconds`
- `POST /api/chat` - chat with manager agent
- `GET /api/state` - retrieve dashboard state

## Deployment notes
You can deploy this side-loaded app from this branch by setting startup command to:
```bash
python manager_agent_app/app.py
```

If your platform expects a requirements file at root, either:
1. configure dependency install path to `manager_agent_app/requirements.txt`, or
2. mirror the same dependencies in a root-level requirements file.
