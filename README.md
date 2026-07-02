# Calcolatore Mutuo 🏠

An Italian mortgage calculator built with [Dash](https://dash.plotly.com/) and
[Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/).
It covers the full purchase journey — from initial costs to long-term rent-vs-buy
analysis — with inverse solvers so you can work backwards from a budget or monthly
payment target.

## Features

| Tab | What it does |
|-----|--------------|
| 📊 **Risultati** | Mortgage KPIs, itemised costs, donut chart, amortisation bar chart |
| 💡 **Cosa Posso Permettermi?** | Grid tables: max home price from budget / payment; min duration; max rate |
| 🏘️ **Affitto vs Acquisto** | NPV analysis, cumulative-cost chart, break-even, inflation sensitivity |
| 📅 **Piano di Ammortamento** | Full monthly schedule + annual summary; residual balance chart |
| 🔍 **Analisi di Sensibilità** | Heatmap (rate × duration), stress test, cost curve, anticipo trade-off |

## Project structure

```
calcolatoremutuo/
├── app.py              # Thin entry point — Dash app + layout + WSGI server
├── core/
│   ├── finance.py      # pmt, build_costs, amortization_schedule
│   └── solvers.py      # Inverse / numerical solvers (brentq)
├── utils/
│   └── __init__.py     # fe(), fp() formatting helpers
├── ui/
│   ├── theme.py        # Global Plotly template + colour palette
│   ├── components.py   # kpi_card, result_badge, info_alert
│   ├── sidebar.py      # build_sidebar()
│   └── tabs.py         # build_tabs()
├── callbacks/
│   ├── __init__.py     # register_all_callbacks(app)
│   ├── shared.py       # SIDEBAR_INPUTS, _safe()
│   ├── sidebar_cb.py   # Slider sync, LTV display, collapse toggle
│   ├── risultati.py    # Tab 1
│   ├── inverse.py      # Tab 2
│   ├── rent.py         # Tab 3
│   ├── amort.py        # Tab 4
│   └── sensitivity.py  # Tab 5
├── assets/
│   └── custom.css      # Inter font, gradient cards, sidebar, tabs
├── requirements.txt
├── vercel.json
└── .gitignore
```

## Local development

```bash
# 1 — create and activate a virtual environment
python -m venv .venv && source .venv/bin/activate

# 2 — install dependencies
pip install -r requirements.txt

# 3 — run the dev server
python app.py
# → http://127.0.0.1:8050
```

## Production (Gunicorn)

```bash
gunicorn app:server --bind 0.0.0.0:8050 --workers 2
```

## Deploy to Vercel

The repo ships with a `vercel.json` that configures Vercel's Python builder.

```bash
# install Vercel CLI if needed
npm i -g vercel

vercel          # follow prompts — framework: Other, build: auto-detected
```

Vercel will use `app:app` (the Flask WSGI object aliased as `app` in `app.py`)
as the HTTP handler.

> **Note**: Vercel free-tier functions have a 10 s timeout. All calculations
> complete well within this limit.
