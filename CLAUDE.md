# CLAUDE.md — AI Assistant Guide for Oneai

## Project Overview

**Oneai** (deployed as `oneaiviz`) is a lightweight Flask web application that visualizes Bitcoin monthly price data using Chart.js. It serves as a proof-of-concept data visualization tool deployed on Microsoft Azure App Service.

- **Language**: Python 3.8
- **Framework**: Flask
- **Deployment**: Azure App Service via GitHub Actions CI/CD
- **Frontend**: Jinja2 templates + Chart.js v1.0.2 (CDN)
- **Live App Name**: `oneaiviz` (Azure)

---

## Repository Structure

```
Oneai/
├── .github/
│   └── workflows/
│       └── master_oneaiviz.yml   # CI/CD: builds and deploys to Azure on push to master
├── templates/                    # Jinja2 HTML templates
│   ├── flask_viz.html            # Home/navigation page with embedded Google Data Studio iframe
│   ├── bar_chart.html            # Bar chart visualization
│   ├── line_chart.html           # Line chart visualization
│   └── pie_chart.html            # Pie chart visualization
├── application.py                # Main Flask app — routes, data, app entry point
├── HelloWorldAzure.py            # Minimal Flask test app (not the production entry point)
└── CLAUDE.md                     # This file
```

---

## Application Entry Point

The production entry point is **`application.py`**. Azure App Service looks for `application.py` by default when deploying Python Flask apps. `HelloWorldAzure.py` is a standalone test file and is not part of the main application.

---

## Routes

All routes are defined in `application.py`. There is no blueprint or router abstraction.

| Route    | Function      | Template         | Description                                      |
|----------|---------------|------------------|--------------------------------------------------|
| `/`      | `flask_viz()` | `flask_viz.html` | Home page with nav links and Google Data Studio  |
| `/home`  | `flask_viz1()`| `flask_viz.html` | Alternative home (passes pie chart data)         |
| `/bar`   | `bar()`       | `bar_chart.html` | Bar chart of Bitcoin monthly prices              |
| `/line`  | `line()`      | `line_chart.html`| Line chart of Bitcoin monthly prices             |
| `/pie`   | `pie()`       | `pie_chart.html` | Pie chart of Bitcoin monthly prices              |

---

## Data Model

There is no database. All data is hardcoded in `application.py` as module-level Python lists:

- **`labels`**: 12 month abbreviations (`'JAN'` through `'DEC'`)
- **`values`**: 12 Bitcoin price floats (USD, historical 2017 data)
- **`colors`**: 12 hex color strings used for pie chart segments

Template variables passed per route:
- `title` — page/chart title string
- `max` — Y-axis ceiling (hardcoded `17000`)
- `labels` — list of month strings (bar/line charts)
- `values` — list of float prices (bar/line charts)
- `set` — `zip(values, labels, colors)` (pie/home charts)

---

## Templates

Templates use **Jinja2** syntax (`{{ }}` for variables, `{% %}` for logic). Chart.js is loaded from CDN in chart templates:

```html
<script src='https://cdnjs.cloudflare.com/ajax/libs/Chart.js/1.0.2/Chart.min.js'></script>
```

Chart data is injected server-side using Jinja2 for-loops inside `<script>` tags. Note: Chart.js **v1.0.2** is used — this is an old API (`new Chart(ctx).Bar(...)`, not the modern `new Chart(ctx, {type: 'bar', ...})`).

Layout uses deprecated `<center>` HTML tags — this is existing style, not a recommended pattern.

---

## CI/CD and Deployment

**Workflow**: `.github/workflows/master_oneaiviz.yml`

- **Trigger**: Push to `master` branch
- **Runner**: `ubuntu-latest`
- **Steps**:
  1. Checkout code
  2. Set up Python 3.8
  3. Build with `azure/appservice-build@v1`
  4. Deploy to Azure Web App `oneaiviz` (production slot)

The deploy secret (`AzureAppService_PublishProfile_...`) is stored in GitHub repository secrets. Never commit Azure publish profile credentials to the repository.

**Branch strategy**:
- `master` — production branch, triggers Azure deployment
- `claude/*` — AI assistant working branches (e.g., `claude/add-claude-documentation-50uik`)

---

## Development Workflow

### Running Locally

There is no `requirements.txt`. Install Flask manually:

```bash
pip install flask
```

Run the application:

```bash
python application.py
```

The app runs on `http://127.0.0.1:5000` by default.

### Making Changes

1. Work on a feature branch (never commit directly to `master` unless deploying)
2. Modify `application.py` for route/data changes
3. Modify files in `templates/` for UI changes
4. Test locally by running `python application.py`
5. Merge to `master` to trigger Azure deployment via GitHub Actions

---

## Key Conventions

- **No test suite exists.** Manual testing via local server is the current approach.
- **No `requirements.txt`.** Flask is the only external dependency.
- **No type hints or docstrings** in existing code — do not add them unless asked.
- **Data is stateless and hardcoded.** There is no persistence layer.
- **Azure entry point**: Azure expects `application.py` (not `app.py` or `main.py`).
- **Python compatibility**: Code uses Python 2/3 compatibility headers (`#!/usr/bin/env python`, `# coding: utf-8`) though Python 3.8 is the target runtime.
- **Variable naming**: Module-level data uses lowercase snake_case (`labels`, `values`, `colors`). Local route variables follow the same pattern (`bar_labels`, `pie_values`, etc.).

---

## Things to Be Careful About

1. **Do not push to `master` directly** unless intending a production deployment — every push to `master` triggers an Azure deploy.
2. **Chart.js v1.0.2 API** is very different from modern Chart.js. Keep chart code consistent with the old API unless upgrading the CDN version too.
3. **The `/home` route** passes pie chart data but renders `flask_viz.html` (the nav page) — this appears intentional for backward compatibility.
4. **The `zip()` in `set=zip(...)` is consumed once** — Jinja2 iterates it once in the template. Do not reuse in the same render call.
5. **No error handling** exists in any route. Keep this in mind when adding new routes.
6. **Azure secret**: `AzureAppService_PublishProfile_2f3b6641592c4eecb48725317f66aff1` must remain in GitHub Secrets only.
