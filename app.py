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
from dash import dcc, html, Input, Output
import requests as _req

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
        dcc.Location(id="_url", refresh=False),
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
                                        html.H2(
                                            "Simulatore acquisto con Mutuo per rendita", className="mb-1"),
                                        html.P(
                                            "Analisi per l'acquisto di un immobile in Italia, a mezzo mutuo e con fini di rendita da locazione.",
                                            className="app-subtitle",
                                        ),
                                    ],
                                    style={"position": "relative",
                                           "zIndex": "1"},
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
        html.Footer(
            html.Small([
                "© 2025 ",
                html.Strong("Dario Esposito"),
                " · Calcolatore Mutuo per Rendita · Tutti i diritti riservati",
                html.Span(" · ", style={"color": "#cbd5e1"}),
                html.Span(id="visit-counter"),
            ]),
            className="text-center text-muted py-3 mt-2",
            style={"borderTop": "1px solid #e2e8f0", "fontSize": "0.72rem",
                   "letterSpacing": "0.03em"},
        ),
    ],
    fluid=True,
    className="px-4",
)

# ── Callbacks ─────────────────────────────────────────────────────────────────
register_all_callbacks(dash_app)


@dash_app.callback(
    Output("visit-counter", "children"),
    Input("_url", "pathname"),
)
def _count_visit(_):
    """Increment CounterAPI on every page load and display the total."""
    try:
        r = _req.get(
            "https://api.counterapi.dev/v1/darioesposito/calcolatoremutuo/up",
            timeout=2,
        )
        n = r.json().get("count")
        return f"{n:,} visite" if isinstance(n, int) else ""
    except Exception:
        return ""

# ── Vercel / Gunicorn WSGI entrypoint ─────────────────────────────────────────
# Vercel's @vercel/python builder looks for a top-level variable named 'app'
# that implements the WSGI interface.  'server' is the Flask app underneath Dash.
app = server  # noqa: F811

# ── Local dev ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    dash_app.run(debug=True, port=8050)
