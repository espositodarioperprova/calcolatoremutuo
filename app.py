#!/usr/bin/env python3
"""
Calcolatore Mutuo — Italian Mortgage Calculator
================================================
Entry point: creates the Dash app, assembles layout, registers callbacks,
and exposes the WSGI ``server`` for Gunicorn / Vercel.

Run locally::

    python app.py              # dev server on http://127.0.0.1:8050
    gunicorn app:server        # production WSGI
"""

import dash
import dash_bootstrap_components as dbc
from dash import html

from ui.theme import apply_theme
from ui.sidebar import build_sidebar
from ui.tabs import build_tabs
from callbacks import register_all_callbacks

# ── App instance ──────────────────────────────────────────────────────────────
dash_app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.FLATLY,
        dbc.icons.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap",
    ],
    suppress_callback_exceptions=True,
    title="Simulatore acquisto con Mutuo per rendita 🏠",
)

# Exposed WSGI application (Gunicorn / Vercel)
server = dash_app.server

# ── Global chart theme ────────────────────────────────────────────────────────
apply_theme()

# ── Layout ────────────────────────────────────────────────────────────────────
dash_app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span(
                                    "🏠",
                                    style={
                                        "fontSize": "2.5rem",
                                        "marginRight": "1rem",
                                        "lineHeight": "1",
                                        "position": "relative",
                                        "zIndex": "1",
                                    },
                                ),
                                html.Div(
                                    [
                                        html.H2("Simulatore acquisto con Mutuo per rendita", className="mb-1"),
                                        html.P(
                                            "Analisi completa per l'acquisto di un immobile in Italia",
                                            className="app-subtitle",
                                        ),
                                    ],
                                    style={"position": "relative", "zIndex": "1"},
                                ),
                            ],
                            className="d-flex align-items-center",
                        ),
                    ],
                    className="app-header",
                )
            )
        ),
        dbc.Row(
            [
                dbc.Col(build_sidebar(), lg=3, className="mb-3"),
                dbc.Col(html.Div(build_tabs(), className="tabs-wrapper"), lg=9),
            ]
        ),
    ],
    fluid=True,
    className="px-4",
)

# ── Callbacks ─────────────────────────────────────────────────────────────────
register_all_callbacks(dash_app)

# ── Vercel / Gunicorn WSGI entrypoint ─────────────────────────────────────────
# Vercel's @vercel/python builder looks for a top-level variable named 'app'
# that implements the WSGI interface.  'server' is the Flask app underneath Dash.
app = server  # noqa: F811

# ── Local dev ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    dash_app.run(debug=True, port=8050)
