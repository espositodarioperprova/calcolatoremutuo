"""Tab 5 — Analisi di Sensibilità: heatmap, stress test, cost curves."""
from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import Output, dcc, html

from core.finance import pmt, build_costs
from utils import fe, fp
from .shared import SIDEBAR_INPUTS, _safe


def register_sensitivity(app) -> None:
    @app.callback(
        Output("tab-sensitivity-content", "children"),
        *SIDEBAR_INPUTS,
    )
    def update_sensitivity(
        offerta, anticipo, durata, tasso, tipo, rendita,
        mediatore, notaio, perizia, ass_inc, ass_vita,
        donaz_cost, kiron_pct, med_pct,
    ):
        offerta = _safe(offerta, 100_000)
        anticipo = _safe(anticipo, 20_000)
        durata_ref = _safe(durata, 30)
        tasso_ref = _safe(tasso, 3.2) / 100
        rendita = _safe(rendita, 206.58)
        notaio = _safe(notaio, 2000)
        perizia = _safe(perizia, 350)
        ass_inc = _safe(ass_inc, 1300)
        ass_vita = _safe(ass_vita, 3500)
        donaz_cost = _safe(donaz_cost, 2500)
        kiron_pct = _safe(kiron_pct, 2) / 100
        med_pct = _safe(med_pct, 4) / 100
        tipo = tipo or "prima"
        mutuo = max(offerta - anticipo, 0)

        # ── 1. Heatmap: monthly payment = f(rate, duration) ───────────────
        rates = np.linspace(0.01, 0.08, 20)
        durations = list(range(10, 36, 1))
        heat = np.array([[pmt(mutuo, r, d) for r in rates] for d in durations])

        heatmap_fig = go.Figure(go.Heatmap(
            z=heat,
            x=[f"{r * 100:.1f}%" for r in rates],
            y=[str(d) for d in durations],
            colorscale="RdYlGn_r",
            text=[[f"\u20ac{v:.0f}" for v in row] for row in heat],
            texttemplate="%{text}",
            textfont={"size": 9},
            colorbar=dict(title="\u20ac/mese"),
        ))
        heatmap_fig.update_layout(
            title=f"Rata mensile (\u20ac) — Mutuo {fe(mutuo)} · tasso \u00d7 durata",
            xaxis_title="Tasso annuo", yaxis_title="Durata (anni)",
            height=420, margin=dict(t=50, b=50, l=60, r=20),
        )

        # ── 2. Rate stress test ────────────────────────────────────────────
        rates_stress = np.linspace(0.005, 0.12, 60)
        payments_stress = [pmt(mutuo, r, durata_ref) for r in rates_stress]

        stress_fig = go.Figure()
        stress_fig.add_trace(go.Scatter(
            x=rates_stress * 100, y=payments_stress, mode="lines",
            line=dict(color="#ef4444", width=2.5),
            fill="tozeroy", fillcolor="rgba(239,68,68,0.12)",
        ))
        stress_fig.add_vline(
            x=tasso_ref * 100, line_dash="dash",
            annotation_text=f"Attuale {fp(tasso_ref)}",
        )
        stress_fig.update_layout(
            title=f"Rata mensile al variare del tasso — Mutuo {fe(mutuo)}, {durata_ref} anni",
            xaxis_title="Tasso annuo (%)", yaxis_title="Rata mensile (\u20ac)",
            height=300, margin=dict(t=50, b=40, l=50, r=20),
        )

        # ── 3. Total initial cost vs home price ────────────────────────────
        pct_anti = anticipo / offerta if offerta > 0 else 0.20
        offerte = np.linspace(50_000, 800_000, 80)
        costs_var = []
        for o in offerte:
            it, _ = build_costs(
                o, o * pct_anti, rendita, tipo, bool(mediatore),
                notaio, perizia, ass_inc, ass_vita, donaz_cost, kiron_pct, med_pct,
            )
            costs_var.append(it["TOTALE INIZIALE"])

        cost_fig = go.Figure()
        cost_fig.add_trace(go.Scatter(
            x=offerte / 1000, y=costs_var, mode="lines",
            line=dict(color="#3b82f6", width=2.5),
        ))
        cost_fig.add_vline(
            x=offerta / 1000, line_dash="dash",
            annotation_text=f"Attuale {fe(offerta, 0)}",
        )
        cost_fig.update_layout(
            title=f"Costo totale iniziale al variare del prezzo (anticipo {fp(pct_anti, 0)})",
            xaxis_title="Prezzo immobile (k\u20ac)", yaxis_title="Costo totale iniziale (\u20ac)",
            height=300, margin=dict(t=50, b=40, l=50, r=20),
        )

        # ── 4. Anticipo trade-off ──────────────────────────────────────────
        pcts_range = np.linspace(0.05, 0.60, 50)
        initials, monthlies = [], []
        for p in pcts_range:
            ant = offerta * p
            it, _ = build_costs(
                offerta, ant, rendita, tipo, bool(mediatore),
                notaio, perizia, ass_inc, ass_vita, donaz_cost, kiron_pct, med_pct,
            )
            initials.append(it["TOTALE INIZIALE"])
            m = max(offerta - ant, 0)
            monthlies.append(pmt(m, tasso_ref, durata_ref))

        tradeoff_fig = go.Figure()
        tradeoff_fig.add_trace(go.Scatter(
            x=pcts_range * 100, y=initials, mode="lines",
            name="Costo iniziale (\u20ac)", line=dict(color="#f59e0b", width=2),
            yaxis="y",
        ))
        tradeoff_fig.add_trace(go.Scatter(
            x=pcts_range * 100, y=monthlies, mode="lines",
            name="Rata mensile (\u20ac)", line=dict(color="#3b82f6", width=2),
            yaxis="y2",
        ))
        tradeoff_fig.add_vline(
            x=pct_anti * 100, line_dash="dash",
            annotation_text=f"Attuale {fp(pct_anti, 0)}",
        )
        tradeoff_fig.update_layout(
            title="Trade-off anticipo: costo iniziale \u2191 \u2192 rata mensile \u2193",
            xaxis_title="% Anticipo",
            yaxis=dict(title="Costo iniziale (\u20ac)", color="#f59e0b"),
            yaxis2=dict(title="Rata mensile (\u20ac)", overlaying="y",
                        side="right", color="#3b82f6"),
            height=300, margin=dict(t=50, b=40, l=60, r=60),
            legend=dict(orientation="h", y=1.1),
        )

        return html.Div([
            dbc.Row([
                dbc.Col(dcc.Graph(figure=heatmap_fig, config={"displayModeBar": False})),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=stress_fig, config={"displayModeBar": False}), md=6),
                dbc.Col(dcc.Graph(figure=cost_fig, config={"displayModeBar": False}), md=6),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=tradeoff_fig, config={"displayModeBar": False})),
            ]),
        ])
