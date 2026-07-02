"""Tab definitions for the main content area."""
from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import html


def build_tabs() -> dbc.Tabs:
    """Return the dbc.Tabs component with all five analysis tabs."""
    return dbc.Tabs(
        [
            dbc.Tab(
                label="📊 Overview sul Mutuo",
                tab_id="tab-risultati",
                children=html.Div(id="tab-risultati-content",
                                  className="pt-3"),
            ),
            dbc.Tab(
                label="📈 Valutazione Investimento",
                tab_id="tab-rent",
                children=html.Div(id="tab-rent-content", className="pt-3"),
            ),
            dbc.Tab(
                label="💡 Cosa Posso Permettermi?",
                tab_id="tab-inverse",
                children=html.Div([
                    # Static spotlight config — always in DOM, survives sidebar changes
                    dbc.Card([
                        dbc.CardHeader(
                            html.H6(
                                [html.I(className="bi bi-sliders me-2"),
                                 "Budget di riferimento personalizzabile"],
                                className="mb-0 fw-bold",
                            ),
                        ),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Budget cash disponibile (€)",
                                              className="small fw-semibold"),
                                    dbc.Input(
                                        id="spotlight-budget",
                                        type="number",
                                        value=50_000,
                                        min=5_000,
                                        step=5_000,
                                    ),
                                ], xs=12, sm=6),
                                dbc.Col([
                                    dbc.Label("% Anticipo di riferimento",
                                              className="small fw-semibold"),
                                    dbc.InputGroup([
                                        dbc.Input(
                                            id="spotlight-pct-ref",
                                            type="number",
                                            value=20,
                                            min=5,
                                            max=60,
                                            step=5,
                                        ),
                                        dbc.InputGroupText("%"),
                                    ]),
                                ], xs=12, sm=6),
                            ]),
                        ]),
                    ], className="mt-3 mb-0 shadow-sm"),
                    html.Div(id="tab-inverse-content"),
                ]),
            ),
            dbc.Tab(
                label="📅 Piano di Ammortamento",
                tab_id="tab-amort",
                children=html.Div(id="tab-amort-content", className="pt-3"),
            ),
            dbc.Tab(
                label="🔍 Analisi di Sensibilità",
                tab_id="tab-sensitivity",
                children=html.Div(
                    id="tab-sensitivity-content", className="pt-3"),
            ),
        ],
        id="main-tabs",
        active_tab="tab-risultati",
    )
