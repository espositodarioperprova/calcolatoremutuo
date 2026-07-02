"""Tab 6 — Estinzione Anticipata: should you pay off the mortgage early?"""
from __future__ import annotations

import numpy as np
from scipy.optimize import brentq
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import Output, Input, dcc, html

from core.finance import pmt, build_costs
from utils import fe, fp
from .shared import SIDEBAR_INPUTS, _safe


def register_estinzione(app) -> None:
    @app.callback(
        Output("tab-estinzione-content", "children"),
        *SIDEBAR_INPUTS,
        Input("anno-estinzione", "value"),
        Input("r-alt",           "value"),
        Input("applica-detraibilita", "value"),
    )
    def update_estinzione(
        offerta, anticipo, durata, tasso, tipo, rendita,
        mediatore, notaio, perizia, ass_inc, ass_vita,
        donaz_cost, kiron_pct, med_pct,
        ass_inc_on, ass_vita_on, donaz_on, kiron_on,
        anno_estinzione, r_alt, applica_detraibilita,
    ):
        # ── Sidebar params ─────────────────────────────────────────────────
        offerta  = _safe(offerta, 100_000)
        anticipo = _safe(anticipo, 20_000)
        durata   = int(_safe(durata, 30))
        tasso_r  = _safe(tasso, 3.2) / 100
        tipo     = tipo or "prima"
        prima    = tipo in ("prima", "prima_donaz")

        mutuo         = max(offerta - anticipo, 0.0)
        monthly_pmt   = pmt(mutuo, tasso_r, durata)
        durata_months = durata * 12

        # ── Tab-specific params ────────────────────────────────────────────
        X         = int(_safe(anno_estinzione, 0) or 0)
        r_alt_v   = _safe(r_alt, 5.0) / 100
        apply_det = bool(applica_detraibilita)

        if X <= 0 or X >= durata:
            return dbc.Alert(
                [
                    html.I(className="bi bi-info-circle me-2"),
                    f"Inserisci un anno di estinzione tra 1 e {durata - 1} "
                    f"(durata mutuo: {durata} anni).",
                ],
                color="info", className="mt-3",
            )

        # ── Remaining balance ──────────────────────────────────────────────
        r_m_mort = tasso_r / 12

        def _remaining(t_months: int) -> float:
            t = min(int(t_months), durata_months)
            if r_m_mort > 0 and durata_months > 0:
                return mutuo * (
                    ((1 + r_m_mort) ** durata_months - (1 + r_m_mort) ** t)
                    / ((1 + r_m_mort) ** durata_months - 1)
                )
            return max(mutuo - monthly_pmt * t, 0.0)

        lump_sum         = _remaining(X * 12)
        remaining_months = (durata - X) * 12
        remaining_years  = durata - X

        # ── Effective mortgage rate (net of tax deductibility if prima casa) ──
        # 19% deductibility on interest paid, up to €4 000/year
        balance_start_X  = _remaining((X - 1) * 12)
        interest_year_X  = balance_start_X * tasso_r
        if apply_det and prima and interest_year_X > 0:
            tax_saving      = min(interest_year_X, 4_000) * 0.19
            eff_saving_rate = tax_saving / max(lump_sum, 1.0)
            eff_rate        = max(tasso_r - eff_saving_rate, 0.0)
        else:
            eff_rate = tasso_r

        # ── NPV of extinguishing at r_alt ─────────────────────────────────
        # NPV(Estingui) = -lump_sum + PV(monthly_pmt for remaining_months at r_alt)
        # Positive → extinguish is better than investing at r_alt
        r_alt_m = (1 + r_alt_v) ** (1 / 12) - 1
        if r_alt_m > 1e-10:
            pv_savings = monthly_pmt * (1 - (1 + r_alt_m) ** (-remaining_months)) / r_alt_m
        else:
            pv_savings = monthly_pmt * remaining_months

        npv_extinguish = -lump_sum + pv_savings

        # ── Breakeven r_alt (= eff_rate, computed numerically) ─────────────
        def _npv_brk(r_m: float) -> float:
            r_m = max(r_m, 1e-10)
            return -lump_sum + monthly_pmt * (1 - (1 + r_m) ** (-remaining_months)) / r_m

        try:
            r_be_m   = brentq(_npv_brk, 1e-10, 0.12 / 12, maxiter=200)
            r_be_ann = (1 + r_be_m) ** 12 - 1
        except Exception:
            r_be_ann = eff_rate  # fallback

        extinguish_better = r_alt_v < r_be_ann

        # ── Chart 1: Annual CF savings (bar chart) ─────────────────────────
        yrs  = list(range(1, durata + 1))
        cf_quo_ann = [-monthly_pmt * 12] * durata
        cf_est_ann = [-monthly_pmt * 12 if yr <= X else 0.0 for yr in yrs]

        cf_fig = go.Figure()
        cf_fig.add_trace(go.Bar(
            x=yrs, y=cf_quo_ann, name="Status quo",
            marker_color="#ef4444", opacity=0.55,
        ))
        cf_fig.add_trace(go.Bar(
            x=yrs, y=cf_est_ann, name=f"Con estinzione all'anno {X}",
            marker_color="#10b981", opacity=0.85,
        ))
        cf_fig.add_vline(x=X + 0.5, line_dash="dash", line_color="#f59e0b",
                         annotation_text=f"Anno {X}: estingui")
        cf_fig.update_layout(
            title=f"Cashflow annuo da mutuo — con e senza estinzione all'anno {X}",
            xaxis_title="Anno", yaxis_title="CF da mutuo (\u20ac/anno)",
            height=320, margin=dict(t=50, b=40, l=60, r=20),
            barmode="overlay",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )

        # ── Chart 2: Cumulative wealth comparison from year X ──────────────
        # wealth_A[m] = -lump_sum + monthly_pmt × m   (savings from extinguishment)
        # wealth_B[m] = lump_sum × ((1+r_alt_m)^m − 1)  (investment gains on same capital)
        m_range    = list(range(0, remaining_months + 1))
        yr_range   = [m / 12 for m in m_range]
        wealth_A   = [-lump_sum + monthly_pmt * m for m in m_range]
        wealth_B   = [lump_sum * ((1 + r_alt_m) ** m - 1) for m in m_range]

        # Find crossover (where A first surpasses B or they equate)
        crossover_yr = None
        for i in range(1, len(m_range)):
            if (wealth_A[i] - wealth_B[i]) * (wealth_A[i - 1] - wealth_B[i - 1]) <= 0:
                crossover_yr = yr_range[i]
                break

        line_a = "#10b981" if extinguish_better else "#ef4444"
        cum_fig = go.Figure()
        cum_fig.add_trace(go.Scatter(
            x=yr_range, y=wealth_A,
            name="Estingui (risparmio cumulato)",
            mode="lines", line=dict(color=line_a, width=2.5),
        ))
        cum_fig.add_trace(go.Scatter(
            x=yr_range, y=wealth_B,
            name=f"Investi a {fp(r_alt_v)} (guadagno cumulato)",
            mode="lines", line=dict(color="#3b82f6", width=2.5),
        ))
        cum_fig.add_hline(y=0, line_dash="dot", line_color="#94a3b8")
        if crossover_yr is not None:
            cum_fig.add_vline(x=crossover_yr, line_dash="dash", line_color="#f59e0b",
                              annotation_text=f"Pareggio ~{crossover_yr:.1f} anni")
        cum_fig.update_layout(
            title=f"Confronto cumulato da anno {X}: Estingui vs Investi a {fp(r_alt_v)}",
            xaxis_title=f"Anni dall'anno {X}",
            yaxis_title="Guadagno/perdita vs status quo (\u20ac)",
            height=360, margin=dict(t=50, b=40, l=60, r=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )

        # ── Chart 3: NPV(Estingui) sensitivity to r_alt ────────────────────
        r_range  = np.linspace(0.001, 0.12, 60)
        npv_sens = []
        for ra in r_range:
            ra_m = (1 + ra) ** (1 / 12) - 1
            if ra_m > 1e-10:
                pv = monthly_pmt * (1 - (1 + ra_m) ** (-remaining_months)) / ra_m
            else:
                pv = monthly_pmt * remaining_months
            npv_sens.append(-lump_sum + pv)

        sens_fig = go.Figure()
        sens_fig.add_trace(go.Scatter(
            x=r_range * 100, y=npv_sens,
            mode="lines", line=dict(color="#8b5cf6", width=2.5),
            fill="tozeroy", fillcolor="rgba(139,92,246,0.12)",
        ))
        sens_fig.add_hline(y=0, line_dash="dot", line_color="#94a3b8",
                           annotation_text="Break-even")
        sens_fig.add_vline(x=r_alt_v * 100, line_dash="dash", line_color="#3b82f6",
                           annotation_text=f"Tuo r_alt {fp(r_alt_v)}")
        sens_fig.add_vline(x=r_be_ann * 100, line_dash="dash", line_color="#f59e0b",
                           annotation_text=f"Breakeven {fp(r_be_ann)}")
        sens_fig.update_layout(
            title="NPV(Estingui) al variare del tasso alternativo — positivo = conviene estinguere",
            xaxis_title="Rendimento alternativo (%)",
            yaxis_title="NPV netto (\u20ac)",
            height=340, margin=dict(t=50, b=40, l=60, r=20),
        )

        # ── KPIs ──────────────────────────────────────────────────────────
        verdict_color = "success" if extinguish_better else "primary"
        det_note = "al netto detraz. 19%" if (apply_det and prima) else "lordo"
        if extinguish_better:
            verdict_txt = (
                f"\u2714\ufe0f  Conviene estinguere — tasso mutuo netto ({fp(eff_rate)}) "
                f"> rendimento alternativo ({fp(r_alt_v)})"
            )
        else:
            verdict_txt = (
                f"\u2139\ufe0f  Meglio investire — rendimento alternativo ({fp(r_alt_v)}) "
                f"> tasso mutuo netto ({fp(eff_rate)})"
            )

        kpis = dbc.Row([
            dbc.Col(html.Div([
                html.Div(f"Saldo residuo anno {X}",
                         style={"fontSize": "0.68rem", "color": "#64748b"}),
                html.Div(fe(lump_sum),
                         style={"fontSize": "1.4rem", "fontWeight": "700", "color": "#ef4444"}),
                html.Small("da versare per estinguere", className="text-muted"),
            ], className="p-3 text-center rounded",
               style={"background": "#f8fafc", "border": "1px solid #e2e8f0"})),
            dbc.Col(html.Div([
                html.Div("Rata mensile liberata",
                         style={"fontSize": "0.68rem", "color": "#64748b"}),
                html.Div(f"+{fe(monthly_pmt, 2)}/mese",
                         style={"fontSize": "1.4rem", "fontWeight": "700", "color": "#10b981"}),
                html.Small(f"per {remaining_years} anni", className="text-muted"),
            ], className="p-3 text-center rounded",
               style={"background": "#f8fafc", "border": "1px solid #e2e8f0"})),
            dbc.Col(html.Div([
                html.Div("Tasso mutuo effettivo",
                         style={"fontSize": "0.68rem", "color": "#64748b"}),
                html.Div(fp(eff_rate),
                         style={"fontSize": "1.4rem", "fontWeight": "700", "color": "#3b82f6"}),
                html.Small(det_note, className="text-muted"),
            ], className="p-3 text-center rounded",
               style={"background": "#f8fafc", "border": "1px solid #e2e8f0"})),
            dbc.Col(html.Div([
                html.Div("Breakeven tasso alternativo",
                         style={"fontSize": "0.68rem", "color": "#64748b"}),
                html.Div(fp(r_be_ann),
                         style={"fontSize": "1.4rem", "fontWeight": "700", "color": "#f59e0b"}),
                html.Small("oltre cui conviene investire", className="text-muted"),
            ], className="p-3 text-center rounded",
               style={"background": "#f8fafc", "border": "1px solid #e2e8f0"})),
        ], className="mb-3 g-3")

        return html.Div([
            kpis,
            dbc.Alert([html.I(className="bi bi-info-circle-fill me-2"), verdict_txt],
                      color=verdict_color, className="mb-3"),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=cf_fig, config={"displayModeBar": False}), md=12),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=cum_fig,  config={"displayModeBar": False}), md=6),
                dbc.Col(dcc.Graph(figure=sens_fig, config={"displayModeBar": False}), md=6),
            ], className="mt-3"),
        ])
