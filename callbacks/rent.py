"""Tab 3 — Affitto vs Acquisto: NPV and break-even analysis."""
from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import Output, Input, dcc, html

from core.finance import pmt, build_costs
from utils import fe, fp
from .shared import SIDEBAR_INPUTS, _safe


def register_rent(app) -> None:
    # ── Layout callback (renders inputs + placeholders) ────────────────────
    @app.callback(
        Output("tab-rent-content", "children"),
        *SIDEBAR_INPUTS,
    )
    def update_rent(
        offerta, anticipo, durata, tasso, tipo, rendita,
        mediatore, notaio, perizia, ass_inc, ass_vita,
        donaz_cost, kiron_pct, med_pct,
    ):
        offerta = _safe(offerta, 100_000)
        anticipo = _safe(anticipo, 20_000)
        durata = _safe(durata, 30)
        tasso_r = _safe(tasso, 3.2) / 100
        rendita = _safe(rendita, 206.58)
        notaio = _safe(notaio, 2000)
        perizia = _safe(perizia, 350)
        ass_inc = _safe(ass_inc, 1300)
        ass_vita = _safe(ass_vita, 3500)
        donaz_cost = _safe(donaz_cost, 2500)
        kiron_pct = _safe(kiron_pct, 2) / 100
        med_pct = _safe(med_pct, 4) / 100
        tipo = tipo or "prima"

        items, _ = build_costs(
            offerta, anticipo, rendita, tipo, bool(mediatore),
            notaio, perizia, ass_inc, ass_vita, donaz_cost, kiron_pct, med_pct,
        )
        costo_iniziale = items["TOTALE INIZIALE"]
        mutuo = max(offerta - anticipo, 0)
        monthly_pmt = pmt(mutuo, tasso_r, durata)

        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H5("Parametri comparazione", className="fw-bold mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Affitto mensile di mercato (€)"),
                            dbc.Input(id="affitto", type="number", value=600, min=0, step=50),
                        ]),
                        dbc.Col([
                            dbc.Label("Inflazione annua (%)"),
                            dbc.InputGroup([
                                dbc.Input(id="inflaz", type="number", value=2.0, min=0, max=20, step=0.1),
                                dbc.InputGroupText("%"),
                            ]),
                        ]),
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Tasso di sconto personale (%)"),
                            dbc.InputGroup([
                                dbc.Input(id="discount", type="number", value=5.0, min=0, max=30, step=0.1),
                                dbc.InputGroupText("%"),
                            ]),
                        ]),
                        dbc.Col([
                            dbc.Label("Costi aggiuntivi affittuario (%)"),
                            dbc.InputGroup([
                                dbc.Input(id="spese-pct", type="number", value=35, min=0, max=100, step=5),
                                dbc.InputGroupText("%"),
                            ]),
                            dbc.FormText("Spese condominiali, assicurazione, manutenzione, sfitto"),
                        ]),
                    ], className="mb-3"),
                    html.Div(id="rent-results"),
                ], md=4),
                dbc.Col(dcc.Graph(id="rent-chart", config={"displayModeBar": False}), md=8),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id="npv-sensitivity-chart", config={"displayModeBar": False}), md=6),
                dbc.Col(dcc.Graph(id="break-even-chart", config={"displayModeBar": False}), md=6),
            ], className="mt-3"),
            dcc.Store(id="rent-store", data={
                "offerta": offerta,
                "costo_iniziale": costo_iniziale,
                "monthly_pmt": monthly_pmt,
                "durata": durata,
            }),
        ])

    # ── Chart / results callback ───────────────────────────────────────────
    @app.callback(
        Output("rent-results", "children"),
        Output("rent-chart", "figure"),
        Output("npv-sensitivity-chart", "figure"),
        Output("break-even-chart", "figure"),
        Input("affitto", "value"),
        Input("inflaz", "value"),
        Input("discount", "value"),
        Input("spese-pct", "value"),
        Input("rent-store", "data"),
    )
    def update_rent_charts(affitto, inflaz, discount, spese_pct, store):
        empty = go.Figure()
        if not store or not affitto:
            return "", empty, empty, empty

        offerta = store["offerta"]
        costo_iniziale = store["costo_iniziale"]
        monthly_pmt_val = store["monthly_pmt"]
        durata = store["durata"]

        affitto = _safe(affitto, 600)
        inflaz_r = _safe(inflaz, 2) / 100
        discount_r = _safe(discount, 5) / 100
        spese_r = _safe(spese_pct, 35) / 100

        n = durata * 12
        r_disc = discount_r / 12
        r_infl = inflaz_r / 12

        buy_cumulative = costo_iniziale
        rent_cumulative = 0.0
        npv_delta = -costo_iniziale

        years_list, buy_cum_list, rent_cum_list, npv_list = [], [], [], []
        break_even_year = None

        for m in range(1, n + 1):
            affitto_m = affitto * (1 + r_infl) ** (m - 1)
            affitto_net = affitto_m * (1 + spese_r)
            buy_cumulative += monthly_pmt_val
            rent_cumulative += affitto_net
            savings = affitto_net - monthly_pmt_val
            npv_delta += savings / (1 + r_disc) ** m
            if m % 12 == 0:
                yr = m // 12
                years_list.append(yr)
                buy_cum_list.append(buy_cumulative)
                rent_cum_list.append(rent_cumulative)
                npv_list.append(npv_delta)
                if break_even_year is None and npv_delta > 0:
                    break_even_year = yr

        future_value = offerta * (1 + inflaz_r) ** durata
        future_value_npv = future_value / (1 + discount_r) ** durata
        final_npv = npv_delta + future_value_npv

        # Cumulative cost chart
        cum_fig = go.Figure()
        cum_fig.add_trace(go.Scatter(
            x=years_list, y=buy_cum_list, name="Acquisto (uscite cumulative)",
            line=dict(color="#ef4444", width=2.5),
        ))
        cum_fig.add_trace(go.Scatter(
            x=years_list, y=rent_cum_list, name="Affitto (uscite cumulative)",
            line=dict(color="#3b82f6", width=2.5),
        ))
        if break_even_year:
            cum_fig.add_vline(
                x=break_even_year, line_dash="dot", line_color="green",
                annotation_text=f"Break-even anno {break_even_year}",
            )
        cum_fig.update_layout(
            title="Costi cumulativi: Acquisto vs Affitto",
            xaxis_title="Anno", yaxis_title="€ (uscite cumulative)",
            height=350, margin=dict(t=50, b=40, l=50, r=20),
            legend=dict(orientation="h", y=1.1),
        )

        # NPV sensitivity over different inflation assumptions
        infls = np.linspace(0, 0.05, 20)
        npv_vals = []
        for inf in infls:
            r_i = inf / 12
            npv_tmp = -costo_iniziale
            for m in range(1, n + 1):
                aff = affitto * (1 + r_i) ** (m - 1) * (1 + spese_r)
                npv_tmp += (aff - monthly_pmt_val) / (1 + r_disc) ** m
            fv = offerta * (1 + inf) ** durata / (1 + discount_r) ** durata
            npv_vals.append(npv_tmp + fv)

        npv_sens_fig = go.Figure(go.Scatter(
            x=infls * 100, y=npv_vals, mode="lines+markers",
            line=dict(color="#10b981", width=2.5),
            fill="tozeroy", fillcolor="rgba(16,185,129,0.12)",
        ))
        npv_sens_fig.add_hline(y=0, line_dash="dash", line_color="red")
        npv_sens_fig.update_layout(
            title="NPV acquisto in funzione dell'inflazione immobiliare",
            xaxis_title="Inflazione (%)", yaxis_title="NPV (€)",
            height=300, margin=dict(t=50, b=40, l=50, r=20),
        )

        # Break-even NPV over time
        npv_fig = go.Figure(go.Scatter(
            x=years_list, y=npv_list, mode="lines",
            line=dict(color="#8b5cf6", width=2.5),
            name="NPV delta (acquisto - affitto)",
        ))
        npv_fig.add_hline(y=0, line_dash="dash", line_color="red",
                          annotation_text="Indifferente")
        npv_fig.update_layout(
            title="NPV netto dell'acquisto (risparmio vs affitto)",
            xaxis_title="Anno", yaxis_title="€",
            height=300, margin=dict(t=50, b=40, l=50, r=20),
        )

        be_text = f"Anno {break_even_year}" if break_even_year else "Non raggiunto"
        results = html.Div([
            html.H6("Risultati analisi", className="fw-bold mt-2"),
            dbc.Table(html.Tbody([
                html.Tr([html.Td("Rata mensile mutuo"), html.Td(fe(monthly_pmt_val, 2))]),
                html.Tr([html.Td("Affitto mensile netto (tot. costi)"),
                         html.Td(fe(affitto * (1 + spese_r), 2))]),
                html.Tr([html.Td("Valore futuro casa (nominale)"), html.Td(fe(future_value))]),
                html.Tr([html.Td("Valore futuro casa (NPV)"), html.Td(fe(future_value_npv))]),
                html.Tr([html.Td("NPV finale acquisto"),
                         html.Td(fe(final_npv),
                                 className=f"fw-bold text-{'success' if final_npv > 0 else 'danger'}")]),
                html.Tr([html.Td("Break-even"), html.Td(be_text, className="fw-bold")]),
            ]), size="sm", bordered=True),
            dbc.Alert(
                "NPV > 0: acquistare è conveniente rispetto ad affittare"
                if final_npv > 0
                else "NPV < 0: affittare è finanziariamente più conveniente",
                color="success" if final_npv > 0 else "warning",
                className="small py-2 mt-2",
            ),
        ])

        return results, cum_fig, npv_sens_fig, npv_fig
