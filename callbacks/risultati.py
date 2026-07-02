"""Tab 1 — Risultati: mortgage summary, cost breakdown, annual chart."""
from __future__ import annotations

import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import Output, dcc, html, dash_table

from core.finance import pmt, build_costs, amortization_schedule
from utils import fe, fp
from ui.components import kpi_card
from ui.theme import PALETTE
from .shared import SIDEBAR_INPUTS, _safe


def register_risultati(app) -> None:
    @app.callback(
        Output("tab-risultati-content", "children"),
        *SIDEBAR_INPUTS,
    )
    def update_risultati(
        offerta, anticipo, durata, tasso, tipo, rendita,
        mediatore, notaio, perizia, ass_inc, ass_vita,
        donaz_cost, kiron_pct, med_pct,
        ass_inc_on, ass_vita_on, donaz_on, kiron_on,
    ):
        offerta = _safe(offerta, 100_000)
        anticipo = _safe(anticipo, 20_000)
        durata = _safe(durata, 30)
        tasso = _safe(tasso, 3.2) / 100
        rendita = _safe(rendita, 206.58)
        notaio = _safe(notaio, 2000)
        perizia = _safe(perizia, 350)
        ass_inc = _safe(ass_inc,    1300) if ass_inc_on != False else 0.0
        ass_vita = _safe(ass_vita,   3500) if ass_vita_on != False else 0.0
        donaz_cost = _safe(donaz_cost, 2500) if donaz_on != False else 0.0
        kiron_pct = (_safe(kiron_pct,  2) / 100) if kiron_on != False else 0.0
        med_pct = _safe(med_pct, 4) / 100

        mutuo = max(offerta - anticipo, 0)
        items, val_cat = build_costs(
            offerta, anticipo, rendita, tipo or "prima",
            bool(mediatore), notaio, perizia, ass_inc, ass_vita,
            donaz_cost, kiron_pct, med_pct,
        )

        monthly = pmt(mutuo, tasso, durata)
        total_paid = monthly * durata * 12
        total_interest = total_paid - mutuo
        prima = tipo in ("prima", "prima_donaz")
        ltv = mutuo / offerta * 100 if offerta > 0 else 0

        # Compute schedule early — used for capped IRPEF benefit and charts
        amort_df = amortization_schedule(mutuo, tasso, durata)

        if prima and not amort_df.empty:
            _ann_int = amort_df.groupby("Anno")["Interessi (€)"].sum()
            deductible_annual = min(float(_ann_int.iloc[0]), 4_000)
            tax_benefit_annual = deductible_annual * 0.19
            # art. 15 TUIR: cap €4 000/anno su interessi passivi detraibili
            tax_benefit_total = float(
                sum(min(yi, 4_000) * 0.19 for yi in _ann_int)
            )
        else:
            tax_benefit_annual = tax_benefit_total = 0.0

        # ── KPI row ────────────────────────────────────────────────────────
        kpi_row = dbc.Row([
            dbc.Col(kpi_card("Mutuo", fe(mutuo),
                    f"LTV {ltv:.1f}%", "primary", "🏦"), md=3),
            dbc.Col(kpi_card("Rata mensile", fe(monthly, 2),
                    f"per {durata} anni", "danger", "📆"), md=3),
            dbc.Col(kpi_card("Costo totale iniziale", fe(
                items["TOTALE INIZIALE"]), "tutto incluso", "warning", "💰"), md=3),
            dbc.Col(kpi_card(
                "Interessi totali", fe(total_interest),
                f"Risparmio fiscale {fe(tax_benefit_total, 0)}" if prima else "Nessuna detrazione",
                "secondary", "📈",
            ), md=3),
        ], className="mb-4")

        # ── Cost table + pie ───────────────────────────────────────────────
        rows_table = [
            {"Voce": k, "Importo": fe(v, 2)}
            for k, v in items.items()
            if v > 0 and k != "TOTALE INIZIALE"
        ]
        rows_table.append({"Voce": "TOTALE INIZIALE",
                          "Importo": fe(items["TOTALE INIZIALE"], 2)})

        pie_labels = [k for k, v in items.items() if v > 0 and k !=
                      "TOTALE INIZIALE"]
        pie_values = [v for k, v in items.items() if v > 0 and k !=
                      "TOTALE INIZIALE"]

        pie_fig = go.Figure(go.Pie(
            labels=pie_labels, values=pie_values,
            hole=0.45, textposition="outside", textinfo="label+percent",
            marker=dict(colors=PALETTE, line=dict(color="white", width=2)),
        ))
        pie_fig.update_layout(
            showlegend=False, margin=dict(t=30, b=10, l=10, r=10),
            height=380, title_text="Composizione costi iniziali", title_x=0.5,
        )

        cost_table = dash_table.DataTable(
            data=rows_table,
            columns=[{"name": "Voce", "id": "Voce"}, {
                "name": "Importo", "id": "Importo"}],
            style_cell={"textAlign": "left",
                        "padding": "8px", "fontFamily": "inherit"},
            style_header={"fontWeight": "bold", "backgroundColor": "#f8fafc"},
            style_data_conditional=[
                {"if": {"filter_query": '{Voce} = "TOTALE INIZIALE"'},
                 "fontWeight": "bold", "backgroundColor": "#fef9c3"},
            ],
            style_table={"overflowX": "auto"},
        )

        breakdown_row = dbc.Row([
            dbc.Col([html.H5("Dettaglio costi iniziali",
                    className="fw-bold mb-3"), cost_table], md=6),
            dbc.Col(dcc.Graph(figure=pie_fig, config={
                    "displayModeBar": False}), md=6),
        ], className="mb-4")

        # ── Amortization annual summary ────────────────────────────────────
        if not amort_df.empty:
            annual = amort_df.groupby("Anno").agg(
                Interessi=("Interessi (€)", "sum"),
                Capitale=("Capitale (€)", "sum"),
            ).reset_index()
            area_fig = go.Figure()
            area_fig.add_trace(go.Bar(x=annual["Anno"], y=annual["Interessi"],
                                      name="Interessi", marker_color="#ef4444"))
            area_fig.add_trace(go.Bar(x=annual["Anno"], y=annual["Capitale"],
                                      name="Capitale", marker_color="#10b981"))
            area_fig.update_layout(
                barmode="stack", title="Composizione rata anno per anno",
                xaxis_title="Anno", yaxis_title="€", height=320,
                margin=dict(t=40, b=40, l=40, r=10),
                legend=dict(orientation="h", y=1.1),
            )
        else:
            area_fig = go.Figure()

        mortgage_info = dbc.Row([
            dbc.Col([
                html.H5("Riepilogo mutuo", className="fw-bold mb-3"),
                dbc.Table(html.Tbody([
                    html.Tr([html.Td("Importo mutuo"), html.Td(
                        fe(mutuo), className="fw-bold")]),
                    html.Tr([html.Td("Tasso annuo"), html.Td(fp(tasso))]),
                    html.Tr([html.Td("Durata"), html.Td(
                        f"{durata} anni ({durata * 12} rate)")]),
                    html.Tr([html.Td("Rata mensile"), html.Td(
                        fe(monthly, 2), className="fw-bold text-danger")]),
                    html.Tr([html.Td("Totale pagato"),
                            html.Td(fe(total_paid))]),
                    html.Tr([html.Td("di cui interessi passivi"),
                            html.Td(fe(total_interest))]),
                    html.Tr([html.Td("Valore catastale"), html.Td(fe(val_cat))]),
                    *([] if not prima else [
                        html.Tr([html.Td("Detrazione fiscale anno 1 (art. 15 TUIR)"),
                                 html.Td(fe(tax_benefit_annual, 0), className="text-success fw-bold")]),
                        html.Tr([html.Td("≈ Risparmio IRPEF mensile"),
                                 html.Td(fe(tax_benefit_annual / 12, 0), className="text-success")]),
                    ]),
                ]), bordered=True, hover=True, size="sm"),
            ], md=5),
            dbc.Col(dcc.Graph(figure=area_fig, config={
                    "displayModeBar": False}), md=7),
        ])

        return html.Div([kpi_row, breakdown_row, mortgage_info])
