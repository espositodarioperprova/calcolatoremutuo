"""Tab definitions for the main content area."""
from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import html


def build_tabs() -> dbc.Tabs:
    """Return the dbc.Tabs component with all five analysis tabs."""
    return dbc.Tabs(
        [
            dbc.Tab(
                label="📊 Risultati",
                tab_id="tab-risultati",
                children=html.Div(id="tab-risultati-content", className="pt-3"),
            ),
            dbc.Tab(
                label="💡 Cosa Posso Permettermi?",
                tab_id="tab-inverse",
                children=html.Div(id="tab-inverse-content", className="pt-3"),
            ),
            dbc.Tab(
                label="🏘️ Affitto vs Acquisto",
                tab_id="tab-rent",
                children=html.Div(id="tab-rent-content", className="pt-3"),
            ),
            dbc.Tab(
                label="📅 Piano di Ammortamento",
                tab_id="tab-amort",
                children=html.Div(id="tab-amort-content", className="pt-3"),
            ),
            dbc.Tab(
                label="🔍 Analisi di Sensibilità",
                tab_id="tab-sensitivity",
                children=html.Div(id="tab-sensitivity-content", className="pt-3"),
            ),
        ],
        id="main-tabs",
        active_tab="tab-risultati",
    )
