"""Tab definitions for the main content area."""
from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import html

from ui.metodologia import build_metodologia_tab


def build_tabs() -> dbc.Tabs:
    """Return the dbc.Tabs component with all six analysis tabs."""
    return dbc.Tabs(
        [
            dbc.Tab(
                id="tab-btn-risultati",
                label="📊 Overview sul Mutuo",
                tab_id="tab-risultati",
                children=html.Div(id="tab-risultati-content",
                                  className="pt-3"),
            ),
            dbc.Tab(
                id="tab-btn-rent",
                label="📈 Valutazione Investimento",
                tab_id="tab-rent",
                children=html.Div(id="tab-rent-content", className="pt-3"),
            ),
            dbc.Tab(
                id="tab-btn-inverse",
                label="💡 Cosa Posso Permettermi?",
                tab_id="tab-inverse",
                children=html.Div([
                    # Static spotlight config — always in DOM
                    dbc.Card([
                        dbc.CardHeader(
                            html.H6(
                                [html.I(className="bi bi-sliders me-2"),
                                 html.Span(id="tabs-inv-budget-hdr", children="Budget di riferimento personalizzabile")],
                                className="mb-0 fw-bold",
                            ),
                        ),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Budget cash disponibile (€)",
                                              id="tabs-inv-budget-cash", className="small fw-semibold"),
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
                                              id="tabs-inv-pct-ref", className="small fw-semibold"),
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
                id="tab-btn-amort",
                label="📅 Piano di Ammortamento",
                tab_id="tab-amort",
                children=html.Div(id="tab-amort-content", className="pt-3"),
            ),
            dbc.Tab(
                id="tab-btn-sensitivity",
                label="🔍 Analisi di Sensibilità",
                tab_id="tab-sensitivity",
                children=html.Div(
                    id="tab-sensitivity-content", className="pt-3"),
            ),
            dbc.Tab(
                id="tab-btn-estinzione",
                label="📐 Estinzione Anticipata",
                tab_id="tab-estinzione",
                children=html.Div([
                    # Static inputs — always in DOM, survive sidebar changes
                    dbc.Card([
                        dbc.CardHeader(
                            html.H6(
                                [html.I(className="bi bi-calculator me-2"),
                                 html.Span(id="tabs-est-hdr", children="Parametri estinzione anticipata")],
                                className="mb-0 fw-bold",
                            ),
                        ),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Anno di estinzione",
                                              id="tabs-est-anno", className="small fw-semibold"),
                                    dbc.InputGroup([
                                        dbc.Input(
                                            id="anno-estinzione",
                                            type="number",
                                            value=None,
                                            placeholder="es. 10",
                                            min=1, max=39, step=1,
                                        ),
                                        dbc.InputGroupText("anni"),
                                    ]),
                                    dbc.FormText(
                                        "Anno in cui estingui il mutuo residuo",
                                        id="tabs-est-anno-ft"),
                                ], xs=12, sm=4),
                                dbc.Col([
                                    dbc.Label("Rendimento investimento alternativo",
                                              id="tabs-est-r-alt", className="small fw-semibold"),
                                    dbc.InputGroup([
                                        dbc.Input(
                                            id="r-alt",
                                            type="number",
                                            value=5.0,
                                            min=0, max=20, step=0.1,
                                        ),
                                        dbc.InputGroupText("%"),
                                    ]),
                                    dbc.FormText(
                                        "Tasso che otterresti investendo il saldo residuo altrove",
                                        id="tabs-est-r-alt-ft"
                                    ),
                                ], xs=12, sm=4),
                                dbc.Col([
                                    dbc.Label("Detraibilità interessi",
                                              id="tabs-est-detr", className="small fw-semibold"),
                                    dbc.Switch(
                                        id="applica-detraibilita",
                                        label="Applica 19% detraibilità (prima casa)",
                                        value=True,
                                        className="mt-1",
                                    ),
                                    dbc.FormText(
                                        "Riduce il tasso effettivo del mutuo (max €4 000/anno)",
                                        id="tabs-est-detr-ft"
                                    ),
                                ], xs=12, sm=4),
                            ]),
                        ]),
                    ], className="mt-3 mb-0 shadow-sm"),
                    html.Div(id="tab-estinzione-content"),
                ]),
            ),
            build_metodologia_tab(),
        ],
        id="main-tabs",
        active_tab="tab-risultati",
    )
