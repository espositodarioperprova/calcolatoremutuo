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
from dash import dcc, html, Input, Output, State
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
        dcc.Store(id="theme-store", storage_type="local", data="light"),
        dcc.Store(id="lang-store", storage_type="local", data="it"),
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
                                            id="app-title",
                             children="Simulatore acquisto con Mutuo per rendita \u2014 IN ITALIA",
                             className="mb-1"),
                                        html.P(
                                            id="app-subtitle",
                                            children="Analisi per l'acquisto di un immobile in Italia, a mezzo mutuo e con fini di rendita da locazione.",
                                            className="app-subtitle",
                                        ),
                                    ],
                                    style={"position": "relative",
                                           "zIndex": "1"},
                                ),
                            ],
                            className="d-flex align-items-center",
                        ),
                        html.Div(
                            [
                                html.Button(
                                    html.Span(id="lang-flag", children="EN"),
                                    id="lang-toggle",
                                    n_clicks=0,
                                    title="Cambia lingua / Switch language",
                                    style={
                                        "background": "rgba(255,255,255,0.15)",
                                        "border": "1px solid rgba(255,255,255,0.3)",
                                        "borderRadius": "10px",
                                        "color": "rgba(255,255,255,0.9)",
                                        "padding": "0.45rem 0.75rem",
                                        "fontSize": "1.05rem",
                                        "cursor": "pointer",
                                        "transition": "background 0.2s",
                                    },
                                ),
                                html.Button(
                                    html.I(id="theme-icon",
                                           className="bi bi-moon-stars-fill"),
                                    id="theme-toggle",
                                    n_clicks=0,
                                    title="Attiva/disattiva dark mode",
                                    style={
                                        "background": "rgba(255,255,255,0.15)",
                                        "border": "1px solid rgba(255,255,255,0.3)",
                                        "borderRadius": "10px",
                                        "color": "rgba(255,255,255,0.9)",
                                        "padding": "0.45rem 0.75rem",
                                        "fontSize": "1.05rem",
                                        "cursor": "pointer",
                                        "transition": "background 0.2s",
                                    },
                                ),
                            ],
                            style={
                                "position": "absolute", "top": "1rem", "right": "1rem",
                                "display": "flex", "gap": "0.5rem", "zIndex": "10",
                            },
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
                "© 2026 ",
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


# ── Language toggle ──────────────────────────────────────────────────────────
dash_app.clientside_callback(
    """
    function(n_clicks, pathname, stored) {
        var triggered = window.dash_clientside.callback_context.triggered;
        var lang;
        if (triggered && triggered.length &&
                triggered[0].prop_id === 'lang-toggle.n_clicks' && n_clicks) {
            lang = (stored === 'en') ? 'it' : 'en';
        } else {
            lang = stored || 'it';
        }
        return [lang, lang === 'en' ? 'IT' : 'EN'];
    }
    """,
    Output("lang-store", "data"),
    Output("lang-flag", "children"),
    Input("lang-toggle", "n_clicks"),
    Input("_url", "pathname"),
    State("lang-store", "data"),
    prevent_initial_call=False,
)

# ── Dark mode toggle ──────────────────────────────────────────────────────────
dash_app.clientside_callback(
    """
    function(n_clicks, pathname, stored) {
        var triggered = window.dash_clientside.callback_context.triggered;
        var theme;
        if (triggered && triggered.length &&
                triggered[0].prop_id === 'theme-toggle.n_clicks' && n_clicks) {
            theme = (stored === 'dark') ? 'light' : 'dark';
        } else {
            theme = stored || 'light';
        }
        document.documentElement.setAttribute('data-bs-theme', theme);
        return [theme, theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill'];
    }
    """,
    Output("theme-store", "data"),
    Output("theme-icon", "className"),
    Input("theme-toggle", "n_clicks"),
    Input("_url", "pathname"),
    State("theme-store", "data"),
    prevent_initial_call=False,
)

# ── Vercel / Gunicorn WSGI entrypoint ─────────────────────────────────────────
# Vercel's @vercel/python builder looks for a top-level variable named 'app'
# that implements the WSGI interface.  'server' is the Flask app underneath Dash.
app = server  # noqa: F811

# ── Local dev ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    dash_app.run(debug=True, port=8050)
