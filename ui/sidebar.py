"""Sidebar layout — all mortgage input parameters."""
from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html


def build_sidebar() -> dbc.Card:
    """Return the sticky sidebar card with all input controls."""
    return dbc.Card(
        [
            dbc.CardHeader(
                html.H5(
                    [html.I(className="bi bi-gear-fill me-2"), "Parametri"],
                    className="mb-0 fw-bold",
                )
            ),
            dbc.CardBody([
                dbc.Label("Prezzo immobile (€)", className="fw-semibold"),
                dbc.Input(
                    id="offerta", type="number",
                    value=100_000, min=10_000, step=5_000, className="mb-1",
                ),
                dcc.Slider(
                    id="offerta-slider", min=50_000, max=1_000_000,
                    step=10_000, value=100_000, marks=None,
                    tooltip={"placement": "bottom", "always_visible": False},
                    className="mb-2",
                ),
                html.Hr(className="my-2"),

                dbc.Label("Anticipo (€)", className="fw-semibold"),
                dbc.Input(
                    id="anticipo", type="number",
                    value=20_000, min=0, step=1_000, className="mb-1",
                ),
                html.Div(id="ltv-display", className="text-muted small mb-2"),
                html.Hr(className="my-2"),

                dbc.Row([
                    dbc.Col([
                        dbc.Label("Durata (anni)", className="fw-semibold"),
                        dbc.Input(
                            id="durata", type="number",
                            value=30, min=5, max=40, step=1,
                        ),
                    ]),
                    dbc.Col([
                        dbc.Label("Tasso annuo", className="fw-semibold"),
                        dbc.InputGroup([
                            dbc.Input(
                                id="tasso", type="number",
                                value=3.20, min=0.10, max=20, step=0.05,
                            ),
                            dbc.InputGroupText("%"),
                        ]),
                    ]),
                ], className="mb-2"),
                html.Hr(className="my-2"),

                dbc.Label("Tipo di acquisto", className="fw-semibold"),
                dbc.RadioItems(
                    id="tipo",
                    options=[
                        {"label": "Prima casa", "value": "prima"},
                        {"label": "Prima casa + donazione nella provenienza",
                         "value": "prima_donaz"},
                        {"label": "Seconda casa / Non prima casa",
                         "value": "seconda"},
                    ],
                    value="prima_donaz",
                    className="small mb-2",
                ),
                html.Hr(className="my-2"),

                dbc.Label("Rendita catastale base (€)", className="fw-semibold"),
                dbc.Input(
                    id="rendita", type="number",
                    value=206.58, min=0, step=0.01, className="mb-1",
                ),
                dbc.FormText("Dalla visura catastale dell'immobile"),
                html.Hr(className="my-2"),

                dbc.Checkbox(
                    id="mediatore",
                    label="Includi provvigione agenzia",
                    value=True,
                    className="mb-2",
                ),

                dbc.Button(
                    [html.I(className="bi bi-sliders me-1"), "Costi personalizzati"],
                    id="adv-toggle", color="light", size="sm",
                    className="w-100 mb-2",
                ),
                dbc.Collapse(
                    dbc.Card(dbc.CardBody([
                        dbc.Label("Notaio (€)"),
                        dbc.Input(id="notaio", type="number",
                                  value=2000, min=0, className="mb-2"),
                        dbc.Label("Perizia immobile (€)"),
                        dbc.Input(id="perizia-val", type="number",
                                  value=350, min=0, className="mb-2"),
                        dbc.Label("Assicurazione incendio (€)"),
                        dbc.Input(id="ass-inc", type="number",
                                  value=1300, min=0, className="mb-2"),
                        dbc.Label("Assicurazione vita (€)"),
                        dbc.Input(id="ass-vita", type="number",
                                  value=3500, min=0, className="mb-2"),
                        dbc.Label("Costo atti donazione (€)"),
                        dbc.Input(id="donaz-cost", type="number",
                                  value=2500, min=0, className="mb-2"),
                        dbc.Label("% mediatore creditizio"),
                        dbc.InputGroup([
                            dbc.Input(id="kiron-pct", type="number",
                                      value=2.0, min=0, max=10, step=0.1),
                            dbc.InputGroupText("%"),
                        ], className="mb-2"),
                        dbc.Label("% agenzia immobiliare"),
                        dbc.InputGroup([
                            dbc.Input(id="med-pct", type="number",
                                      value=4.0, min=0, max=10, step=0.1),
                            dbc.InputGroupText("%"),
                        ]),
                    ]), className="border-0"),
                    id="adv-collapse",
                    is_open=False,
                ),
            ]),
        ],
        className="sidebar-card",
        style={"position": "sticky", "top": "10px"},
    )
