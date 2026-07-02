"""Tab 2 — Valutazione Investimento: comprehensive buy-to-let ROI analysis."""
from __future__ import annotations

import numpy as np
from scipy.optimize import brentq
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import Output, Input, dcc, html

from core.finance import pmt, build_costs
from ui.components import kpi_card
from utils import fe, fp
from .shared import SIDEBAR_INPUTS, _safe

# Tax on gross effective rent by regime
_TAX = {
    "cc10":    0.100,         # Cedolare secca agevolata 10%
    "cs21":    0.210,         # Cedolare secca 21%
    "irpef35": 0.35 * 0.95,  # IRPEF 35% on 95% of rent
    "irpef43": 0.43 * 0.95,  # IRPEF 43% on 95% of rent
}


def register_rent(app) -> None:
    # ── Layout callback (renders inputs + chart placeholders) ─────────────
    @app.callback(
        Output("tab-rent-content", "children"),
        *SIDEBAR_INPUTS,
    )
    def update_rent(
        offerta, anticipo, durata, tasso, tipo, rendita,
        mediatore, notaio, perizia, ass_inc, ass_vita,
        donaz_cost, kiron_pct, med_pct,
        ass_inc_on, ass_vita_on, donaz_on, kiron_on,
    ):
        offerta = _safe(offerta, 100_000)
        anticipo = _safe(anticipo, 20_000)
        durata = _safe(durata, 30)
        tasso_r = _safe(tasso, 3.2) / 100
        rendita_val = _safe(rendita, 206.58)
        notaio = _safe(notaio, 2000)
        perizia = _safe(perizia, 350)
        ass_inc   = _safe(ass_inc,    1300) if ass_inc_on  != False else 0.0
        ass_vita  = _safe(ass_vita,   3500) if ass_vita_on != False else 0.0
        donaz_cost = _safe(donaz_cost, 2500) if donaz_on   != False else 0.0
        kiron_pct = (_safe(kiron_pct,  2) / 100) if kiron_on != False else 0.0
        med_pct = _safe(med_pct, 4) / 100
        tipo = tipo or "prima_donaz"

        items, _ = build_costs(
            offerta, anticipo, rendita_val, tipo, bool(mediatore),
            notaio, perizia, ass_inc, ass_vita, donaz_cost, kiron_pct, med_pct,
        )
        costo_iniziale = items["TOTALE INIZIALE"]
        mutuo = max(offerta - anticipo, 0)
        monthly_pmt_val = pmt(mutuo, tasso_r, durata)

        # Sensible default: gross yield ~4.8% → 0.4% of price per month
        default_affitto = max(round(offerta * 0.004 / 50) * 50, 300)
        # Default IMU rate: 0 for prima casa (entrambe le categorie), 0.96% per seconda
        default_imu = 0.0 if tipo in ("prima", "prima_donaz") else 0.96
        imu_default_ann = rendita_val * 1.05 * 160 * default_imu / 100
        if imu_default_ann > 0:
            imu_formula_text = (
                f"Rendita × 1.05 × 160 × {default_imu:.2f}% → "
                f"{fe(imu_default_ann, 0)}/anno · {fe(imu_default_ann / 12, 1)}/mese"
            )
        else:
            imu_formula_text = "Prima casa: esente da IMU (art. 13 c.2 D.L. 201/2011)"

        return html.Div([
            dbc.Row([
                # ── Left: input panel ─────────────────────────────────────
                dbc.Col([
                    html.H5("Parametri investimento", className="fw-bold mb-3"),

                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Affitto mensile lordo (€)"),
                            dbc.Input(id="affitto", type="number",
                                      value=default_affitto, min=0, step=50),
                        ]),
                        dbc.Col([
                            dbc.Label("Regime fiscale locazione"),
                            dbc.Select(
                                id="regime-tassazione",
                                options=[
                                    {"label": "10% — Canone Concordato", "value": "cc10"},
                                    {"label": "21% — Cedolare Secca",    "value": "cs21"},
                                    {"label": "35% — IRPEF (penult. scaglione)", "value": "irpef35"},
                                    {"label": "43% — IRPEF (ultimo scaglione)",  "value": "irpef43"},
                                ],
                                value="cs21",
                                className="form-select",
                            ),
                        ]),
                    ], className="mb-2"),

                    dbc.Row([
                        dbc.Col([
                            dbc.Label([
                                "Tasso al quale scontare cashflow futuri (%)",
                                html.Span(" ⓘ", id="tooltip-discount-target",
                                          style={"cursor": "pointer", "color": "#64748b"}),
                            ]),
                            dbc.Tooltip(
                                html.Div([
                                    html.P("Costo opportunità del capitale.", className="fw-semibold mb-1"),
                                    html.Ul([
                                        html.Li("BTP decennale: ~3.5% (risk-free)"),
                                        html.Li("Portafoglio bilanciato: ~5–6%"),
                                        html.Li("Mercato azionario: ~7–8%"),
                                    ], className="mb-1 ps-3 small"),
                                    html.P("Più è alto, più penalizzi ritorni a lungo termine.",
                                           className="mb-0 small"),
                                ]),
                                target="tooltip-discount-target",
                                placement="right",
                            ),
                            dbc.InputGroup([
                                dbc.Input(id="discount", type="number",
                                          value=5.0, min=0, max=30, step=0.1),
                                dbc.InputGroupText("%"),
                            ]),
                        ]),
                        dbc.Col([
                            dbc.Label("Rivalutazione immobile (%/anno)"),
                            dbc.InputGroup([
                                dbc.Input(id="inflaz", type="number",
                                          value=2.0, min=0, max=20, step=0.1),
                                dbc.InputGroupText("%"),
                            ]),
                        ]),
                    ], className="mb-2"),

                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Vacancy rate (% tempo sfitto)"),
                            dbc.InputGroup([
                                dbc.Input(id="vacancy-pct", type="number",
                                          value=5, min=0, max=100, step=1),
                                dbc.InputGroupText("%"),
                            ]),
                        ]),
                        dbc.Col([
                            dbc.Label("Spese fisse annue (€)"),
                            dbc.Input(id="spese-fisse", type="number",
                                      value=1800, min=0, step=100),
                            dbc.FormText("Condominio, TARI, gestione, assicurazione"),
                        ]),
                    ], className="mb-2"),

                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Manutenzione ordinaria (%/anno sul valore)"),
                            dbc.InputGroup([
                                dbc.Input(id="manutenzione-ord-pct", type="number",
                                          value=0.5, min=0, max=5, step=0.1),
                                dbc.InputGroupText("%"),
                            ]),
                            dbc.FormText("~0.5–1% del valore/anno"),
                        ]),
                        dbc.Col([
                            dbc.Label("Manutenzione straordinaria"),
                            dbc.InputGroup([
                                dbc.Input(id="manutenzione-freq", type="number",
                                          value=0.2, min=0, max=5, step=0.05,
                                          placeholder="ev/anno"),
                                dbc.InputGroupText("ev/anno"),
                            ], className="mb-1"),
                            dbc.InputGroup([
                                dbc.Input(id="manutenzione-costo", type="number",
                                          value=3000, min=0, step=500,
                                          placeholder="€/evento"),
                                dbc.InputGroupText("€/ev"),
                            ]),
                            dbc.FormText("es. 0.2 ev/anno × €3 000 = €600/anno"),
                        ]),
                    ], className="mb-2"),

                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Aliquota IMU (%/anno — A/2·A/3·A/4 coeff. 160)"),
                            dbc.InputGroup([
                                dbc.Input(id="imu-rate", type="number",
                                          value=default_imu, min=0, max=3, step=0.01),
                                dbc.InputGroupText("%"),
                            ]),
                            dbc.FormText(imu_formula_text),
                        ]),
                        dbc.Col([
                            dbc.Label("Costi dismissione/vendita (% valore finale)"),
                            dbc.InputGroup([
                                dbc.Input(id="costo-vendita-pct", type="number",
                                          value=4.0, min=0, max=15, step=0.5),
                                dbc.InputGroupText("%"),
                            ]),
                            dbc.FormText("Agenzie, notaio, imposte plusvalenza"),
                        ]),
                    ], className="mb-3"),

                    html.Div(id="investment-results"),
                ], md=5),

                # ── Right: waterfall chart ────────────────────────────────
                dbc.Col(
                    dcc.Graph(id="waterfall-chart", config={"displayModeBar": False}),
                    md=7,
                ),
            ]),

            dbc.Row([
                dbc.Col(dcc.Graph(id="cumulative-return-chart",
                                  config={"displayModeBar": False}), md=6),
                dbc.Col(dcc.Graph(id="npv-apprezz-chart",
                                  config={"displayModeBar": False}), md=6),
            ], className="mt-3"),

            dbc.Row([
                dbc.Col(dcc.Graph(id="irr-rent-chart",
                                  config={"displayModeBar": False}), md=12),
            ], className="mt-3"),

            dcc.Store(id="rent-store", data={
                "offerta":       offerta,
                "mutuo":         mutuo,
                "costo_iniziale": costo_iniziale,
                "monthly_pmt":   monthly_pmt_val,
                "durata":        durata,
                "rendita":       rendita_val,
                "tipo":          tipo,
                "tasso_r":       tasso_r,
            }),
        ])

    # ── Results + charts callback ──────────────────────────────────────────
    @app.callback(
        Output("investment-results",    "children"),
        Output("waterfall-chart",       "figure"),
        Output("cumulative-return-chart", "figure"),
        Output("npv-apprezz-chart",     "figure"),
        Output("irr-rent-chart",        "figure"),
        Input("affitto",               "value"),
        Input("regime-tassazione",     "value"),
        Input("discount",              "value"),
        Input("inflaz",                "value"),
        Input("vacancy-pct",           "value"),
        Input("spese-fisse",           "value"),
        Input("manutenzione-ord-pct",  "value"),
        Input("manutenzione-freq",     "value"),
        Input("manutenzione-costo",    "value"),
        Input("imu-rate",              "value"),
        Input("costo-vendita-pct",     "value"),
        Input("rent-store",            "data"),
    )
    def update_investment(
        affitto, regime, discount, inflaz, vacancy_pct, spese_fisse,
        maint_ord_pct, maint_freq, maint_costo, imu_rate_input,
        costo_vendita_pct, store,
    ):
        _empty = go.Figure().update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
        )
        if not store or not affitto:
            return "", _empty, _empty, _empty, _empty

        # ── Unpack store ───────────────────────────────────────────────────
        offerta          = store["offerta"]
        mutuo_val        = store["mutuo"]
        costo_iniziale   = store["costo_iniziale"]
        monthly_pmt_val  = store["monthly_pmt"]
        durata           = store["durata"]
        rendita_val      = store.get("rendita", 206.58)
        tipo             = store.get("tipo", "prima_donaz")
        tasso_r          = store.get("tasso_r", 0.032)

        # ── Parameters ────────────────────────────────────────────────────
        affitto_lordo    = _safe(affitto, 800)
        tax_r            = _TAX.get(regime or "cs21", _TAX["cs21"])
        discount_r       = _safe(discount, 5)  / 100
        inflaz_r         = _safe(inflaz, 2)    / 100
        vacancy_r        = _safe(vacancy_pct, 5) / 100
        spese_fisse_ann  = _safe(spese_fisse, 1800)
        maint_ord_r      = _safe(maint_ord_pct, 0.5) / 100
        maint_freq_v     = _safe(maint_freq, 0.2)
        maint_costo_v    = _safe(maint_costo, 3000)
        imu_r            = _safe(imu_rate_input, 0.0 if tipo == "prima" else 0.96) / 100
        sell_cost_r      = _safe(costo_vendita_pct, 4) / 100

        # ── Monthly cash-flow components ──────────────────────────────────
        # Effective rent (after vacancy)
        affitto_eff      = affitto_lordo * (1 - vacancy_r)
        vacancy_drag     = affitto_lordo - affitto_eff
        tax_mensile      = affitto_eff * tax_r
        affitto_netto    = affitto_eff - tax_mensile

        # Operating costs
        imu_ann          = rendita_val * 1.05 * 160 * imu_r
        imu_mens         = imu_ann / 12
        maint_ord_mens   = (offerta * maint_ord_r) / 12
        maint_ext_mens   = (maint_freq_v * maint_costo_v) / 12
        spese_fisse_mens = spese_fisse_ann / 12
        costi_op_mens    = imu_mens + maint_ord_mens + maint_ext_mens + spese_fisse_mens

        net_cf_mens      = affitto_netto - monthly_pmt_val - costi_op_mens

        # ── Annual figures ─────────────────────────────────────────────────
        aff_lordo_ann    = affitto_lordo * 12
        aff_eff_ann      = affitto_eff   * 12
        aff_netto_ann    = affitto_netto * 12
        costi_op_ann     = costi_op_mens * 12
        net_cf_ann       = net_cf_mens   * 12

        # ── Key investment metrics ─────────────────────────────────────────
        gross_yield  = aff_lordo_ann / offerta
        noi_pretax   = aff_eff_ann - costi_op_ann          # Cap Rate basis
        cap_rate     = noi_pretax / offerta
        noi_posttax  = aff_netto_ann - costi_op_ann        # Net yield basis
        net_yield    = noi_posttax / offerta
        coc_return   = net_cf_ann / costo_iniziale

        # Break-even gross monthly rent → net_cf = 0
        denom = max((1 - vacancy_r) * (1 - tax_r), 1e-6)
        break_even_rent = (monthly_pmt_val + costi_op_mens) / denom

        # ── Monthly series (rent + costs grow with inflation) ──────────────
        n_months      = int(durata) * 12
        r_inf_m       = (1 + inflaz_r) ** (1 / 12) - 1
        r_disc_m      = (1 + discount_r) ** (1 / 12) - 1

        cfs = []
        for m in range(1, n_months + 1):
            growth      = (1 + r_inf_m) ** (m - 1)
            rent_eff_m  = affitto_eff * growth
            net_rent_m  = rent_eff_m * (1 - tax_r)
            ops_m       = costi_op_mens * growth
            cfs.append(net_rent_m - monthly_pmt_val - ops_m)

        # Terminal sale value
        prop_final    = offerta * (1 + inflaz_r) ** durata
        terminal_cf   = prop_final * (1 - sell_cost_r)

        # ── IRR (annualised) ───────────────────────────────────────────────
        def _npv(r_m: float) -> float:
            if r_m <= -1.0:
                return float("inf")
            npv = -costo_iniziale
            discount_vec = (1 + r_m) ** np.arange(1, n_months + 1)
            npv += float(np.sum(np.array(cfs) / discount_vec))
            npv += terminal_cf / (1 + r_m) ** n_months
            return npv

        try:
            r_irr_m   = brentq(_npv, -0.09 / 12, 0.5 / 12, maxiter=300)
            irr_ann   = (1 + r_irr_m) ** 12 - 1
        except Exception:
            irr_ann   = None

        # ── NPV at discount rate ───────────────────────────────────────────
        disc_vec = (1 + r_disc_m) ** np.arange(1, n_months + 1)
        npv_total = (-costo_iniziale
                     + float(np.sum(np.array(cfs) / disc_vec))
                     + terminal_cf / (1 + r_disc_m) ** n_months)

        # ── Remaining mortgage balance at year t ───────────────────────────
        r_m_mort = tasso_r / 12
        n_m_mort = int(durata) * 12
        def _remaining(t_months: int) -> float:
            if r_m_mort > 0:
                return mutuo_val * (
                    ((1 + r_m_mort) ** n_m_mort - (1 + r_m_mort) ** t_months)
                    / ((1 + r_m_mort) ** n_m_mort - 1)
                )
            return max(mutuo_val - monthly_pmt_val * t_months, 0.0)

        # ── CHART 1: Waterfall — monthly CF decomposition ─────────────────
        wf_labels = [
            "Affitto lordo", "Vacancy", "Imposte",
            "Manutenzione", "Spese fisse", "IMU",
            "Rata mutuo", "Cashflow netto",
        ]
        wf_values = [
            affitto_lordo,
            -vacancy_drag,
            -tax_mensile,
            -(maint_ord_mens + maint_ext_mens),
            -spese_fisse_mens,
            -imu_mens,
            -monthly_pmt_val,
            net_cf_mens,
        ]
        waterfall_fig = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute", "relative", "relative",
                     "relative", "relative", "relative",
                     "relative", "total"],
            x=wf_labels,
            y=wf_values,
            connector={"line": {"color": "#cbd5e1"}},
            increasing={"marker": {"color": "#10b981"}},
            decreasing={"marker": {"color": "#ef4444"}},
            totals={"marker": {"color": "#3b82f6" if net_cf_mens >= 0 else "#ef4444"}},
            texttemplate="%{y:,.0f} €",
            textposition="outside",
        ))
        waterfall_fig.update_layout(
            title=f"Scomposizione cashflow mensile — Affitto lordo {fe(affitto_lordo, 0)}/mese",
            height=420,
            margin=dict(t=50, b=40, l=50, r=20),
            showlegend=False,
        )

        # ── CHART 2: Cumulative P&L over time ─────────────────────────────
        years       = list(range(0, int(durata) + 1))
        cum_cf      = 0.0
        cum_cfs_yr  = []
        equity_gain = []   # property equity - initial investment
        total_pnl   = []

        for yr in years:
            if yr > 0:
                m0 = (yr - 1) * 12
                m1 = yr * 12
                cum_cf += sum(cfs[m0:m1])

            prop_val_yr   = offerta * (1 + inflaz_r) ** yr
            remaining_yr  = _remaining(yr * 12)
            net_equity_yr = prop_val_yr - remaining_yr - costo_iniziale

            cum_cfs_yr.append(cum_cf)
            equity_gain.append(net_equity_yr)
            total_pnl.append(cum_cf + net_equity_yr)

        cum_fig = go.Figure()
        cum_fig.add_trace(go.Scatter(
            x=years, y=cum_cfs_yr, name="Cashflow operativi cumulati",
            mode="lines", line=dict(color="#3b82f6", width=2),
        ))
        cum_fig.add_trace(go.Scatter(
            x=years, y=equity_gain, name="Guadagno netto sull'equity",
            mode="lines", line=dict(color="#10b981", width=2),
        ))
        cum_fig.add_trace(go.Scatter(
            x=years, y=total_pnl, name="P&L totale (se venduto ora)",
            mode="lines+markers", line=dict(color="#f59e0b", width=2.5),
            marker=dict(size=5),
        ))
        cum_fig.add_hline(y=0, line_dash="dot", line_color="#94a3b8",
                          annotation_text="Break-even")
        cum_fig.update_layout(
            title="P&L cumulato nel tempo (rivalutazione + cashflow − investimento iniziale)",
            xaxis_title="Anno", yaxis_title="€",
            height=380, margin=dict(t=50, b=40, l=60, r=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )

        # ── CHART 3: NPV vs appreciation rate ─────────────────────────────
        apprezz_range = np.linspace(-0.02, 0.07, 30)
        npv_range     = []
        for inf in apprezz_range:
            r_i_m = (1 + inf) ** (1 / 12) - 1
            cfs_i = []
            for m in range(1, n_months + 1):
                g        = (1 + r_i_m) ** (m - 1)
                cfs_i.append(affitto_eff * g * (1 - tax_r)
                             - monthly_pmt_val
                             - costi_op_mens * g)
            term_i = offerta * (1 + inf) ** durata * (1 - sell_cost_r)
            dv     = (1 + r_disc_m) ** np.arange(1, n_months + 1)
            npv_i  = (-costo_iniziale
                      + float(np.sum(np.array(cfs_i) / dv))
                      + term_i / (1 + r_disc_m) ** n_months)
            npv_range.append(npv_i)

        npv_fig = go.Figure()
        npv_fig.add_trace(go.Scatter(
            x=apprezz_range * 100, y=npv_range,
            mode="lines", line=dict(color="#8b5cf6", width=2.5),
            fill="tozeroy",
            fillcolor="rgba(139,92,246,0.12)",
        ))
        npv_fig.add_hline(y=0, line_dash="dot", line_color="#94a3b8")
        npv_fig.add_vline(
            x=inflaz_r * 100, line_dash="dash",
            annotation_text=f"Attuale {fp(inflaz_r)}",
        )
        npv_fig.update_layout(
            title=f"NPV vs rivalutazione immobile (tasso sconto {fp(discount_r)})",
            xaxis_title="Rivalutazione annua (%)",
            yaxis_title="NPV (€)",
            height=380, margin=dict(t=50, b=40, l=60, r=20),
        )

        # ── CHART 4: IRR vs monthly rent level ────────────────────────────
        rent_range  = np.linspace(max(affitto_lordo * 0.5, 200), affitto_lordo * 2, 25)
        irr_range   = []
        for rent in rent_range:
            eff   = rent * (1 - vacancy_r)
            cf1   = eff * (1 - tax_r) - monthly_pmt_val - costi_op_mens

            def _npv_r(r_m: float) -> float:
                if r_m <= -1.0:
                    return float("inf")
                dv  = (1 + r_m) ** np.arange(1, n_months + 1)
                return (-costo_iniziale
                        + cf1 * float(np.sum(1.0 / dv))
                        + terminal_cf / (1 + r_m) ** n_months)
            try:
                rm = brentq(_npv_r, -0.09 / 12, 0.5 / 12, maxiter=200)
                irr_range.append((1 + rm) ** 12 - 1)
            except Exception:
                irr_range.append(None)

        irr_valid = [(r, v) for r, v in zip(rent_range, irr_range) if v is not None]
        irr_fig = go.Figure()
        if irr_valid:
            rx, ry = zip(*irr_valid)
            irr_fig.add_trace(go.Scatter(
                x=list(rx), y=[v * 100 for v in ry],
                mode="lines", line=dict(color="#06b6d4", width=2.5),
                fill="tozeroy", fillcolor="rgba(6,182,212,0.12)",
            ))
        irr_fig.add_hline(y=0, line_dash="dot", line_color="#94a3b8")
        irr_fig.add_vline(
            x=affitto_lordo, line_dash="dash",
            annotation_text=f"Affitto attuale {fe(affitto_lordo, 0)}",
        )
        irr_fig.update_layout(
            title="IRR al variare del canone mensile lordo (costante nel tempo)",
            xaxis_title="Affitto lordo mensile (€)",
            yaxis_title="IRR annualizzato (%)",
            height=340, margin=dict(t=50, b=40, l=60, r=20),
        )

        # ── KPI cards ─────────────────────────────────────────────────────
        irr_str  = fp(irr_ann) if irr_ann is not None else "n/d"
        cf_color = "success" if net_cf_mens >= 0 else "danger"
        coc_color = "success" if coc_return >= 0 else "danger"

        kpis = dbc.Row([
            dbc.Col(kpi_card("Cashflow netto/mese",
                             f"{net_cf_mens:+,.0f} €", None, cf_color,    "bi-cash-coin"), md=3),
            dbc.Col(kpi_card("Gross Yield",
                             fp(gross_yield),           None, "primary",   "bi-percent"), md=3),
            dbc.Col(kpi_card("Cap Rate (NOI/valore)",
                             fp(cap_rate),              None, "secondary", "bi-building"), md=3),
            dbc.Col(kpi_card("IRR (su mutuo completo)",
                             irr_str,                   None, coc_color,  "bi-graph-up"), md=3),
        ], className="mb-3")

        # ── Detail metrics table ───────────────────────────────────────────
        rows = [
            ("Affitto lordo mensile",        fe(affitto_lordo, 2)),
            ("Perdita da vacancy",            f"− {fe(vacancy_drag, 2)}"),
            ("Imposte sul canone",            f"− {fe(tax_mensile, 2)}"),
            ("Manutenzione ord. mensile",     f"− {fe(maint_ord_mens, 2)}"),
            ("Manutenzione straord. mensile", f"− {fe(maint_ext_mens, 2)}"),
            ("Spese fisse mensili",           f"− {fe(spese_fisse_mens, 2)}"),
            ("IMU mensile",                   f"− {fe(imu_mens, 2)}"),
            ("Rata mutuo",                    f"− {fe(monthly_pmt_val, 2)}"),
            ("Cashflow netto mensile",        f"{'▲' if net_cf_mens>=0 else '▼'} {fe(abs(net_cf_mens), 2)}"),
            ("─", "─"),
            ("Gross Rental Yield",            fp(gross_yield)),
            ("Cap Rate (pre-tax NOI/valore)", fp(cap_rate)),
            ("Net Yield (post-tax NOI/val.)", fp(net_yield)),
            ("Cash-on-Cash Return",           fp(coc_return)),
            ("IRR (su durata mutuo)",         irr_str),
            ("NPV totale (tasso sconto)",     fe(npv_total)),
            ("Canone break-even",             fe(break_even_rent, 0) + " €/mese"),
        ]

        detail_table = dbc.Table(
            html.Tbody([
                html.Tr([
                    html.Td(label, className="small"),
                    html.Td(value, className="small text-end fw-semibold"),
                ])
                for label, value in rows
            ]),
            size="sm", bordered=True, hover=True, responsive=True,
            className="mb-0",
        )

        return (
            html.Div([kpis, detail_table]),
            waterfall_fig, cum_fig, npv_fig, irr_fig,
        )
