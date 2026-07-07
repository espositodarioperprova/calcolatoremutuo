"""Tab 4 — Piano di Ammortamento: monthly and annual schedule."""
from __future__ import annotations

import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, dash_table

from core.finance import amortization_schedule
from utils.i18n import t
from .shared import SIDEBAR_INPUTS, _safe


def register_amort(app) -> None:
    @app.callback(
        Output("tab-amort-content", "children"),
        *SIDEBAR_INPUTS,
        Input("lang-store", "data"),
    )
    def update_amort(
        offerta, anticipo, durata, tasso, tipo, rendita,
        mediatore, notaio, perizia, ass_inc, ass_vita,
        donaz_cost, kiron_pct, med_pct,
        ass_inc_on, ass_vita_on, donaz_on, kiron_on,
        lang,
    ):
        offerta = _safe(offerta, 100_000)
        anticipo = _safe(anticipo, 20_000)
        durata = _safe(durata, 30)
        tasso_r = _safe(tasso, 3.2) / 100

        mutuo = max(offerta - anticipo, 0)
        df = amortization_schedule(mutuo, tasso_r, durata)
        if df.empty:
            return dbc.Alert(t("amort.invalid", lang), color="warning")

        # Annual summary table
        annual = (
            df.groupby("Anno")
            .agg(
                Rata_totale=("Rata (\u20ac)", "sum"),
                Interessi=("Interessi (\u20ac)", "sum"),
                Capitale=("Capitale (\u20ac)", "sum"),
                Saldo_fine=("Saldo residuo (\u20ac)", "last"),
            )
            .reset_index()
        )
        annual.columns = [
            "Anno", "Rate totali (\u20ac)", "Interessi (\u20ac)",
            "Capitale (\u20ac)", "Saldo a fine anno (\u20ac)",
        ]
        _col = {
            "Anno": t("amort.col.anno", lang),
            "Rate totali (\u20ac)": t("amort.col.rata_totale", lang),
            "Interessi (\u20ac)": t("amort.col.interessi_euro", lang),
            "Capitale (\u20ac)": t("amort.col.capitale_euro", lang),
            "Saldo a fine anno (\u20ac)": t("amort.col.saldo_fine", lang),
            "Mese": t("amort.col.mese", lang),
            "Rata (\u20ac)": t("amort.col.rata_euro", lang),
            "Saldo residuo (\u20ac)": t("amort.col.saldo_residuo", lang),
        }
        annual = annual.round(2)

        # Residual balance chart
        balance_fig = go.Figure()
        balance_fig.add_trace(go.Scatter(
            x=df["Mese"] / 12, y=df["Saldo residuo (\u20ac)"],
            mode="lines", name=t("amort.chart.balance_series", lang),
            line=dict(color="#ef4444", width=2),
            fill="tozeroy", fillcolor="rgba(239,68,68,0.12)",
        ))
        balance_fig.update_layout(
            title=t("amort.chart.balance_title", lang),
            xaxis_title=t("amort.chart.anno", lang), yaxis_title="\u20ac",
            height=280, margin=dict(t=50, b=40, l=50, r=20),
        )

        # Interest vs capital per instalment
        ic_fig = go.Figure()
        ic_fig.add_trace(go.Scatter(
            x=df["Mese"] / 12, y=df["Interessi (\u20ac)"],
            mode="lines", name=t("amort.chart.interessi", lang),
            line=dict(color="#ef4444"),
            fill="tozeroy", fillcolor="rgba(239,68,68,0.22)",
        ))
        ic_fig.add_trace(go.Scatter(
            x=df["Mese"] / 12, y=df["Capitale (\u20ac)"],
            mode="lines", name=t("amort.chart.capitale", lang),
            line=dict(color="#10b981"),
            fill="tozeroy", fillcolor="rgba(16,185,129,0.22)",
        ))
        ic_fig.update_layout(
            title=t("amort.chart.ic_title", lang),
            xaxis_title=t("amort.chart.anno", lang), yaxis_title="\u20ac",
            height=280, margin=dict(t=50, b=40, l=50, r=20),
            legend=dict(orientation="h", y=1.1),
        )

        annual_table = dash_table.DataTable(
            data=annual.to_dict("records"),
            columns=[{"name": _col.get(c, c), "id": c} for c in annual.columns],
            style_cell={"textAlign": "right",
                        "padding": "6px 10px", "fontFamily": "inherit"},
            style_cell_conditional=[
                {"if": {"column_id": "Anno"}, "textAlign": "center"}],
            style_header={"fontWeight": "bold", "backgroundColor": "#f8fafc"},
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "#fafbff"},
            ],
            page_size=10,
            style_table={"overflowX": "auto"},
        )

        monthly_table = dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[{"name": _col.get(c, c), "id": c} for c in df.columns],
            style_cell={
                "textAlign": "right", "padding": "5px 8px",
                "fontFamily": "inherit", "fontSize": "0.85rem",
            },
            style_cell_conditional=[
                {"if": {"column_id": c}, "textAlign": "center"} for c in ["Mese", "Anno"]
            ],
            style_header={"fontWeight": "bold", "backgroundColor": "#f8fafc"},
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "#fafbff"},
            ],
            page_size=24,
            style_table={"overflowX": "auto"},
        )

        return html.Div([
            dbc.Row([
                dbc.Col(dcc.Graph(figure=balance_fig, config={
                        "displayModeBar": False}), md=6),
                dbc.Col(dcc.Graph(figure=ic_fig, config={
                        "displayModeBar": False}), md=6),
            ], className="mb-4"),
            html.H5(t("amort.section.annual", lang), className="fw-bold mb-2"),
            annual_table,
            html.H5(t("amort.section.monthly", lang), className="fw-bold mb-2 mt-4"),
            monthly_table,
        ])
