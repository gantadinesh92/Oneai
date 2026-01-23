# Oneai Flask Charts

This repository contains a small Flask application that renders a landing page and several chart views for Bitcoin monthly prices. It includes templates for pie, bar, and line charts, plus a simple "Hello World" entry point used for Azure demos.

## Project layout

- `application.py` — main Flask app with routes for the chart pages.
- `templates/` — HTML templates for the chart views.
- `HelloWorldAzure.py` — minimal Flask app for a basic Azure deployment test.

## Getting started

### Prerequisites

- Python 3.8+
- `pip`

### Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install flask
```

### Run the chart application

```bash
python application.py
```

Then open:

- `http://127.0.0.1:5000/` (landing page)
- `http://127.0.0.1:5000/pie`
- `http://127.0.0.1:5000/bar`
- `http://127.0.0.1:5000/line`

### Run the Azure hello world app

```bash
python HelloWorldAzure.py
```

Then open:

- `http://127.0.0.1:5000/`

## Notes

The chart pages use static values embedded in the Flask app for demonstration purposes.
