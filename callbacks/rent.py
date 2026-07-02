"""Tab 2 — Valutazione Investimento: comprehensive buy-to-let ROI analysis."""
from __future__ import annotations

import numpy as np
from scipy.optimize import brentq
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import Output, Input, dcc, html

from core.finance import pmt, build_costs
from utils import fe, fp
from .shared import SIDEBAR_INPUTS, _safe

_TAX = {
    "cc10":    0.100,
    "cs21":    0.210,
    "irpef35": 0.35 * 0.95,
    "irpef43": 0.43 * 0.95,
}
_BTP_REF = 0.035  # BTP decennale reference for comparison badge


def register_rent(app) -> None:
    # ── Layout callback ────────────────────────────────────────────────────
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
        offerta   = _safe(offerta, 100_000)
        anticipo  = _safe(anticipo, 20_000)
        durata    = _safe(durata, 30)
        tasso_r   = _safe(tasso, 3.2) / 100
        rendita_v = _safe(rendita, 206.58)
        notaio    = _safe(notaio, 2000)
        perizia   = _safe(perizia, 350)
        ass_inc   = _safe(ass_inc,    1300) if ass_inc_on  != False else 0.0
        ass_vita  = _safe(ass_vita,   3500) if ass_vita_on != False else 0.0
        donaz_c   = _safe(donaz_cost, 2500) if donaz_on    != False else 0.0
        kiron     = (_safe(kiron_pct, 2) / 100) if kiron_on != False else 0.0
        med_pct   = _safe(med_pct, 4) / 100
        tipo      = tipo or "prima_donaz"

        items, _ = build_costs(
            offerta, anticipo, rendita_v, tipo, bool(mediatore),
            notaio, perizia, ass_inc, ass_vita, donaz_c, kiron, med_pct,
        )
        costo_iniziale = items["TOTALE INIZIALE"]
        mutuo          = max(offerta - anticipo, 0)
        monthly_pmt_v  = pmt(mutuo, tasso_r, durata)

        default_affitto = max(round(offerta * 0.004 / 50) * 50, 300)
        default_imu     = 0.0 if tipo in ("prima", "prima_donaz") else 0.96
        imu_default_ann = rendita_v * 1.05 * 160 * default_imu / 100
        if imu_default_ann > 0:
            imu_text = (
                f"Rendita \u00d7 1.05 \u00d7 160 \u00d7 {default_imu:.2f}% \u2192 "
                f"{fe(imu_default_ann, 0)}/anno \u00b7 {fe(imu_default_ann / 12, 1)}/mese"
            )
        else:
            imu_text = "Prima casa: esente da IMU (art. 13 c.2 D.L. 201/2011)"

        return html.Div([
            dbc.Row([
                # ── Left: inputs ──────────────────────────────────────────
                dbc.Col([
                    html.H5("Parametri investimento", className="fw-bold mb-3"),

                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Affitto mensile lordo (\u20ac)"),
                            dbc.Input(id="affitto", type="number",
                                      value=default_affitto, min=0, step=50),
                        ]),
                        dbc.Col([
                            dbc.Label("Regime fiscale locazione"),
                            dbc.Select(
                                id="regime-tassazione",
                                options=[
                                    {"label": "10% \u2014 Canone Concordato", "value": "cc10"},
                                    {"label": "21% \u2014 Cedolare Secca",    "value": "cs21"},
                                    {"label": "35% \u2014 IRPEF (penult.)",   "value": "irpef35"},
                                    {"label": "43% \u2014 IRPEF (ultimo)",    "value": "irpef43"},
                                ],
                                value="cs21", className="form-select",
                            ),
                        ]),
                    ], className="mb-2"),

                    dbc.Row([
                        dbc.Col([
                            dbc.Label([
                                "Tasso di sconto cashflow futuri (%)",
                                html.Span(" \u24d8", id="tooltip-discount-target",
                                          style={"cursor": "pointer", "color": "#64748b"}),
                            ]),
                            dbc.Tooltip(
                                html.Div([
                                    html.P("Costo opportunit\u00e0 del capitale.", className="fw-semibold mb-1"),
                                    html.Ul([
                                        html.Li("BTP decennale: ~3.5% (risk-free)"),
                                        html.Li("Portafoglio bilanciato: ~5\u20136%"),
                                        html.Li("Mercato azionario: ~7\u20138%"),
                                    ], className="mb-1 ps-3 small"),
                                    html.P("Pi\u00f9 \u00e8 alto, pi\u00f9 penalizzi ritorni a lungo termine.",
                                           className="mb-0 small"),
                                ]),
                                target="tooltip-discount-target", placement="right",
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
                            dbc.Label("Spese fisse annue (\u20ac)"),
                            dbc.Input(id="spese-fisse", type="number",
                                      value=1800, min=0, step=100),
                            dbc.FormText("Condominio, TARI, gestione, assicurazione"),
                        ]),
                    ], className="mb-2"),

                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Manutenzione ordinaria (%/anno)"),
                            dbc.InputGroup([
                                dbc.Input(id="manutenzione-ord-pct", type="number",
                                          value=0.5, min=0, max=5, step=0.1),
                                dbc.InputGroupText("%"),
                            ]),
                            dbc.FormText("~0.5\u20131% del valore/anno"),
                        ]),
                        dbc.Col([
                            dbc.Label("Manutenzione straordinaria"),
                            dbc.InputGroup([
                                dbc.Input(id="manutenzione-freq", type="number",
                                          value=0.2, min=0, max=5, step=0.05),
                                dbc.InputGroupText("ev/anno"),
                            ], className="mb-1"),
                            dbc.InputGroup([
                                dbc.Input(id="manutenzione-costo", type="number",
                                          value=3000, min=0, step=500),
                                dbc.InputGroupText("\u20ac/ev"),
                            ]),
                            dbc.FormText("0.2 ev/anno \u00d7 \u20ac3\u202f000 = \u20ac600/anno"),
                        ]),
                    ], className="mb-2"),

                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Ricerca inquilino"),
                            dbc.InputGroup([
                                dbc.Input(id="ricerca-costo", type="number",
                                          value=500, min=0, step=100),
                                dbc.InputGroupText("\u20ac/evento"),
                            ], className="mb-1"),
                            dbc.InputGroup([
                                dbc.Input(id="ricerca-freq", type="number",
                                          value=0.5, min=0, max=5, step=0.1),
                                dbc.InputGroupText("eventi/anno"),
                            ]),
                            dbc.FormText("0.5 = ogni 2 anni"),
                        ]),
                        dbc.Col([
                            dbc.Label("Aliquota IMU (%/anno \u2014 A/2\u00b7A/3\u00b7A/4 coeff.\u00a0160)"),
                            dbc.InputGroup([
                                dbc.Input(id="imu-rate", type="number",
                                          value=default_imu, min=0, max=3, step=0.01),
                                dbc.InputGroupText("%"),
                            ]),
                            dbc.FormText(imu_text),
                        ]),
                    ], className="mb-2"),

                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Costi vendita (% valore finale)"),
                            dbc.InputGroup([
                                dbc.Input(id="costo-vendita-pct", type="number",
                                          value=4.0, min=0, max=15, step=0.5),
                                dbc.InputGroupText("%"),
                            ]),
                            dbc.FormText("Agenzie, notaio, eventuali imposte"),
                        ]),
                        dbc.Col([
                            dbc.Label("Anno di uscita (opzionale)"),
                            dbc.InputGroup([
                                dbc.Input(id="anno-uscita", type="number",
                                          value=None,
                                          placeholder=f"default: {int(durata)}",
                                          min=1, max=60, step=1),
                                dbc.InputGroupText("anni"),
                            ]),
                            dbc.FormText(
                                f"Vuoto = {int(durata)} anni. "
                                f"< {int(durata)}: vendita anticipata + saldo residuo detratto. "
                                f"> {int(durata)}: CF post-mutuo inclusi."
                            ),
                        ]),
                    ], className="mb-2"),

                    # ── Crescita canone section ────────────────────────────
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col(
                                    html.Small("Crescita canone di locazione",
                                               className="fw-semibold text-muted"),
                                ),
                                dbc.Col(
                                    dbc.Switch(
                                        id="canone-disallacciato", value=False,
                                        label="Disallaccia dall'inflazione",
                                        className="mb-0",
                                    ),
                                    className="col-auto",
                                ),
                            ], className="align-items-center mb-2"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Crescita (%/anno)", className="small"),
                                    dbc.InputGroup([
                                        dbc.Input(id="canone-growth-pct", type="number",
                                                  value=2.0, min=0, max=20, step=0.1,
                                                  disabled=True),
                                        dbc.InputGroupText("%"),
                                    ]),
                                ]),
                                dbc.Col([
                                    dbc.Label("Adeguamento ogni (anni)", className="small"),
                                    dbc.InputGroup([
                                        dbc.Input(id="canone-step-years", type="number",
                                                  value=2, min=1, max=10, step=1,
                                                  disabled=True),
                                        dbc.InputGroupText("anni"),
                                    ]),
                                    dbc.FormText("Libero: 2 \u00b7 Concordato: 4"),
                                ]),
                            ]),
                        ], className="py-2"),
                    ], className="mb-3 border", style={"borderRadius": "8px"}),

                    html.Div(id="investment-results"),
                ], md=5),

                # ── Right: waterfall chart ─────────────────────────────────
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
                "offerta":        offerta,
                "mutuo":          mutuo,
                "costo_iniziale": costo_iniziale,
                "monthly_pmt":    monthly_pmt_v,
                "durata":         durata,
                "rendita":        rendita_v,
                "tipo":           tipo,
                "tasso_r":        tasso_r,
            }),
        ])

    # ── Investment analysis callback ───────────────────────────────────────
    @app.callback(
        Output("investment-results",      "children"),
        Output("waterfall-chart",         "figure"),
        Output("cumulative-return-chart", "figure"),
        Output("npv-apprezz-chart",       "figure"),
        Output("irr-rent-chart",          "figure"),
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
        Input("anno-uscita",           "value"),
        Input("canone-disallacciato",  "value"),
        Input("canone-growth-pct",     "value"),
        Input("canone-step-years",     "value"),
        Input("ricerca-costo",         "value"),
        Input("ricerca-freq",          "value"),
        Input("rent-store",            "data"),
    )
    def update_investment(
        affitto, regime, discount, inflaz, vacancy_pct, spese_fisse,
        maint_ord_pct, maint_freq, maint_costo, imu_rate_input,
        costo_vendita_pct,
        anno_uscita,
        canone_disallacciato, canone_growth_pct, canone_step_years,
        ricerca_costo, ricerca_freq,
        store,
    ):
        _empty = go.Figure().update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        if not store or not affitto:
            return "", _empty, _empty, _empty, _empty

        # ── Unpack store ───────────────────────────────────────────────────
        offerta         = store["offerta"]
        mutuo_val       = store["mutuo"]
        costo_iniziale  = store["costo_iniziale"]
        monthly_pmt_val = store["monthly_pmt"]
        durata          = store["durata"]
        rendita_val     = store.get("rendita", 206.58)
        tipo            = store.get("tipo", "prima_donaz")
        tasso_r         = store.get("tasso_r", 0.032)

        # ── Parameters ────────────────────────────────────────────────────
        affitto_lordo   = _safe(affitto, 800)
        tax_r           = _TAX.get(regime or "cs21", _TAX["cs21"])
        discount_r      = _safe(discount, 5)    / 100
        inflaz_r        = _safe(inflaz, 2)      / 100
        vacancy_r       = _safe(vacancy_pct, 5) / 100
        spese_fisse_ann = _safe(spese_fisse, 1800)
        maint_ord_r     = _safe(maint_ord_pct, 0.5) / 100
        maint_freq_v    = _safe(maint_freq, 0.2)
        maint_costo_v   = _safe(maint_costo, 3000)
        imu_r           = _safe(imu_rate_input, 0.0 if tipo == "prima" else 0.96) / 100
        sell_cost_r     = _safe(costo_vendita_pct, 4) / 100
        ricerca_mens    = _safe(ricerca_costo, 500) * _safe(ricerca_freq, 0.5) / 12

        # Anno di uscita
        T = max(int(_safe(anno_uscita, None) or durata), 1)

        # Canone growth parameters
        if canone_disallacciato:
            canone_growth_ann = _safe(canone_growth_pct, 2.0) / 100
            step_yrs          = max(int(_safe(canone_step_years, 2)), 1)
        else:
            canone_growth_ann = inflaz_r
            step_yrs          = 1

        # ── Base monthly components ────────────────────────────────────────
        affitto_eff   = affitto_lordo * (1 - vacancy_r)
        vacancy_drag  = affitto_lordo - affitto_eff
        tax_mensile   = affitto_eff * tax_r
        affitto_netto = affitto_eff - tax_mensile

        imu_ann          = rendita_val * 1.05 * 160 * imu_r
        imu_mens         = imu_ann / 12
        maint_ord_mens   = (offerta * maint_ord_r) / 12
        maint_ext_mens   = (maint_freq_v * maint_costo_v) / 12
        spese_fisse_mens = spese_fisse_ann / 12
        costi_op_base    = (imu_mens + maint_ord_mens + maint_ext_mens
                            + spese_fisse_mens + ricerca_mens)

        net_cf_mens = affitto_netto - monthly_pmt_val - costi_op_base

        # ── Base KPI figures ───────────────────────────────────────────────
        aff_lordo_ann  = affitto_lordo * 12
        aff_eff_ann    = affitto_eff   * 12
        aff_netto_ann  = affitto_netto * 12
        costi_op_ann   = costi_op_base * 12
        gross_yield    = aff_lordo_ann / offerta
        noi_pretax     = aff_eff_ann - costi_op_ann
        cap_rate       = noi_pretax / offerta
        noi_posttax    = aff_netto_ann - costi_op_ann
        net_yield      = noi_posttax / offerta
        net_cf_ann     = net_cf_mens * 12
        coc_return     = net_cf_ann / costo_iniziale
        denom          = max((1 - vacancy_r) * (1 - tax_r), 1e-6)
        break_even_rent = (monthly_pmt_val + costi_op_base) / denom

        # ── Monthly CF series over T years ─────────────────────────────────
        n_months_T    = T * 12
        r_inf_m       = (1 + inflaz_r) ** (1 / 12) - 1
        r_disc_m      = (1 + discount_r) ** (1 / 12) - 1
        durata_months = int(durata) * 12

        cfs = []
        for m in range(1, n_months_T + 1):
            yr_0 = (m - 1) // 12
            if canone_disallacciato:
                n_steps     = yr_0 // step_yrs
                rent_growth = (1 + canone_growth_ann) ** (n_steps * step_yrs)
            else:
                rent_growth = (1 + r_inf_m) ** (m - 1)

            net_rent_m = affitto_eff * rent_growth * (1 - tax_r)
            ops_m      = costi_op_base * (1 + r_inf_m) ** (m - 1)
            mort_m     = monthly_pmt_val if m <= durata_months else 0.0
            cfs.append(net_rent_m - mort_m - ops_m)

        # ── Remaining mortgage balance ─────────────────────────────────────
        r_m_mort = tasso_r / 12

        def _remaining(t_months: int) -> float:
            t = min(int(t_months), durata_months)
            if r_m_mort > 0 and durata_months > 0:
                return mutuo_val * (
                    ((1 + r_m_mort) ** durata_months - (1 + r_m_mort) ** t)
                    / ((1 + r_m_mort) ** durata_months - 1)
                )
            return max(mutuo_val - monthly_pmt_val * t, 0.0)

        # ── Terminal value at year T ───────────────────────────────────────
        prop_at_T    = offerta * (1 + inflaz_r) ** T
        remain_at_T  = _remaining(T * 12)
        net_terminal = prop_at_T * (1 - sell_cost_r) - remain_at_T
        underwater   = net_terminal < 0 and T < int(durata)

        # ── IRR ────────────────────────────────────────────────────────────
        cfs_arr = np.array(cfs)

        def _npv(r_m: float) -> float:
            if r_m <= -1.0:
                return float("inf")
            dv = (1 + r_m) ** np.arange(1, n_months_T + 1)
            return (-costo_iniziale
                    + float(np.sum(cfs_arr / dv))
                    + net_terminal / (1 + r_m) ** n_months_T)

        try:
            r_irr_m = brentq(_npv, -0.09 / 12, 0.5 / 12, maxiter=300)
            irr_ann = (1 + r_irr_m) ** 12 - 1
        except Exception:
            irr_ann = None

        # ── NPV ────────────────────────────────────────────────────────────
        dv        = (1 + r_disc_m) ** np.arange(1, n_months_T + 1)
        npv_total = (-costo_iniziale
                     + float(np.sum(cfs_arr / dv))
                     + net_terminal / (1 + r_disc_m) ** n_months_T)

        # ── Chart 1: Waterfall ─────────────────────────────────────────────
        wf_x = ["Affitto lordo", "Vacancy", "Imposte", "Manutenzione", "Spese fisse"]
        wf_y = [affitto_lordo, -vacancy_drag, -tax_mensile,
                -(maint_ord_mens + maint_ext_mens), -spese_fisse_mens]
        wf_m = ["absolute", "relative", "relative", "relative", "relative"]

        if imu_mens > 0.01:
            wf_x.append("IMU");             wf_y.append(-imu_mens);        wf_m.append("relative")
        if ricerca_mens > 0.01:
            wf_x.append("Ricerca inq.");    wf_y.append(-ricerca_mens);    wf_m.append("relative")
        wf_x.append("Rata mutuo");          wf_y.append(-monthly_pmt_val); wf_m.append("relative")
        wf_x.append("CF netto");            wf_y.append(net_cf_mens);      wf_m.append("total")

        waterfall_fig = go.Figure(go.Waterfall(
            orientation="v", measure=wf_m, x=wf_x, y=wf_y,
            connector={"line": {"color": "#cbd5e1"}},
            increasing={"marker": {"color": "#10b981"}},
            decreasing={"marker": {"color": "#ef4444"}},
            totals={"marker": {"color": "#3b82f6" if net_cf_mens >= 0 else "#ef4444"}},
            texttemplate="%{y:,.0f} \u20ac", textposition="outside",
        ))
        waterfall_fig.update_layout(
            title=f"Cashflow mensile (anno\u00a01) \u2014 Affitto lordo {fe(affitto_lordo, 0)}/mese",
            height=420, margin=dict(t=50, b=40, l=50, r=20), showlegend=False,
        )

        # ── Chart 2: Cumulative P&L ────────────────────────────────────────
        years      = list(range(0, T + 1))
        cum_cf     = 0.0
        cum_cfs_yr = []
        equity_gain = []
        total_pnl   = []

        for yr in years:
            if yr > 0:
                cum_cf += sum(cfs[(yr - 1) * 12: yr * 12])
            prop_val_yr   = offerta * (1 + inflaz_r) ** yr
            remaining_yr  = _remaining(yr * 12)
            net_equity_yr = prop_val_yr - remaining_yr - costo_iniziale
            cum_cfs_yr.append(cum_cf)
            equity_gain.append(net_equity_yr)
            total_pnl.append(cum_cf + net_equity_yr)

        cum_fig = go.Figure()
        cum_fig.add_trace(go.Scatter(x=years, y=cum_cfs_yr, name="CF operativi cumulati",
            mode="lines", line=dict(color="#3b82f6", width=2)))
        cum_fig.add_trace(go.Scatter(x=years, y=equity_gain, name="Guadagno netto equity",
            mode="lines", line=dict(color="#10b981", width=2)))
        cum_fig.add_trace(go.Scatter(x=years, y=total_pnl, name="P&L totale (se venduto ora)",
            mode="lines+markers", line=dict(color="#f59e0b", width=2.5), marker=dict(size=5)))
        cum_fig.add_hline(y=0, line_dash="dot", line_color="#94a3b8", annotation_text="Break-even")
        if T != int(durata):
            cum_fig.add_vline(x=T, line_dash="dash", line_color="#ef4444",
                              annotation_text=f"Uscita anno\u00a0{T}")
        cum_fig.update_layout(
            title=f"P&L cumulato \u2014 orizzonte {T} anni",
            xaxis_title="Anno", yaxis_title="\u20ac", height=380,
            margin=dict(t=50, b=40, l=60, r=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )

        # ── Chart 3: NPV vs appreciation ──────────────────────────────────
        apprezz_range = np.linspace(-0.02, 0.07, 30)
        npv_range = []
        for inf in apprezz_range:
            term_i = offerta * (1 + inf) ** T * (1 - sell_cost_r) - _remaining(T * 12)
            npv_i  = (-costo_iniziale
                      + float(np.sum(cfs_arr / dv))
                      + term_i / (1 + r_disc_m) ** n_months_T)
            npv_range.append(npv_i)

        npv_fig = go.Figure()
        npv_fig.add_trace(go.Scatter(x=apprezz_range * 100, y=npv_range,
            mode="lines", line=dict(color="#8b5cf6", width=2.5),
            fill="tozeroy", fillcolor="rgba(139,92,246,0.12)"))
        npv_fig.add_hline(y=0, line_dash="dot", line_color="#94a3b8")
        npv_fig.add_vline(x=inflaz_r * 100, line_dash="dash",
                          annotation_text=f"Attuale {fp(inflaz_r)}")
        npv_fig.update_layout(
            title=f"NPV vs rivalutazione \u2014 sconto {fp(discount_r)}, orizzonte {T} anni",
            xaxis_title="Rivalutazione annua (%)", yaxis_title="NPV (\u20ac)",
            height=380, margin=dict(t=50, b=40, l=60, r=20),
        )

        # ── Chart 4: IRR vs rent level ─────────────────────────────────────
        rent_range = np.linspace(max(affitto_lordo * 0.5, 200), affitto_lordo * 2, 25)
        irr_range  = []
        for rent in rent_range:
            cf1 = rent * (1 - vacancy_r) * (1 - tax_r) - monthly_pmt_val - costi_op_base

            def _npv_r(r_m: float) -> float:
                if r_m <= -1.0:
                    return float("inf")
                dv2 = (1 + r_m) ** np.arange(1, n_months_T + 1)
                return (-costo_iniziale
                        + cf1 * float(np.sum(1.0 / dv2))
                        + net_terminal / (1 + r_m) ** n_months_T)
            try:
                rm = brentq(_npv_r, -0.09 / 12, 0.5 / 12, maxiter=200)
                irr_range.append((1 + rm) ** 12 - 1)
            except Exception:
                irr_range.append(None)

        irr_valid = [(r, v) for r, v in zip(rent_range, irr_range) if v is not None]
        irr_fig   = go.Figure()
        if irr_valid:
            rx, ry = zip(*irr_valid)
            irr_fig.add_trace(go.Scatter(x=list(rx), y=[v * 100 for v in ry],
                mode="lines", line=dict(color="#06b6d4", width=2.5),
                fill="tozeroy", fillcolor="rgba(6,182,212,0.12)"))
        irr_fig.add_hline(y=0, line_dash="dot", line_color="#94a3b8")
        irr_fig.add_vline(x=affitto_lordo, line_dash="dash",
                          annotation_text=f"Attuale {fe(affitto_lordo, 0)}")
        irr_fig.update_layout(
            title=f"IRR al variare del canone \u2014 orizzonte {T} anni",
            xaxis_title="Affitto lordo mensile (\u20ac)", yaxis_title="IRR annualizzato (%)",
            height=340, margin=dict(t=50, b=40, l=60, r=20),
        )

        # ── Hero IRR ──────────────────────────────────────────────────────
        if irr_ann is not None:
            irr_vs_btp  = irr_ann - _BTP_REF
            sign        = "+" if irr_vs_btp >= 0 else ""
            irr_color   = "#10b981" if irr_ann >= discount_r else "#ef4444"
            irr_badge   = f"{sign}{irr_vs_btp * 100:.1f}\u202fpp vs BTP 3.5%"
            irr_display = f"{irr_ann * 100:.2f}%"
            verdict     = ("Investimento solido \u2714"
                           if irr_ann >= discount_r
                           else "Rendimento sotto il tuo obiettivo \u2718")
        else:
            irr_color   = "#94a3b8"
            irr_badge   = "n/d"
            irr_display = "n/d"
            verdict     = "IRR non calcolabile con questi parametri"

        hero_irr = html.Div([
            html.Div("IRR investimento", style={
                "fontSize": "0.72rem", "color": "#64748b",
                "textTransform": "uppercase", "letterSpacing": "0.07em",
                "marginBottom": "4px",
            }),
            html.Div(irr_display, style={
                "fontSize": "3.0rem", "fontWeight": "800",
                "color": irr_color, "lineHeight": "1.0",
            }),
            html.Div(irr_badge, style={
                "fontSize": "0.85rem", "color": irr_color,
                "fontWeight": "600", "marginTop": "2px",
            }),
            html.Div(verdict, style={
                "fontSize": "0.78rem", "color": "#475569",
                "fontWeight": "500", "marginTop": "6px",
            }),
            html.Div([
                html.Span("Orizzonte:\u00a0", style={"color": "#94a3b8"}),
                html.Span(f"{T} anni", className="fw-semibold"),
                html.Span("\u00a0\u00b7\u00a0NPV:\u00a0", style={"color": "#94a3b8"}),
                html.Span(fe(npv_total), className="fw-semibold",
                          style={"color": "#10b981" if npv_total >= 0 else "#ef4444"}),
            ], style={"fontSize": "0.78rem", "marginTop": "6px", "color": "#64748b"}),
        ], className="text-center p-3 mb-3", style={
            "background": f"linear-gradient(135deg, {irr_color}12, {irr_color}25)",
            "border": f"2px solid {irr_color}50",
            "borderRadius": "14px",
        })

        alerts = []
        if underwater:
            alerts.append(dbc.Alert([
                html.I(className="bi bi-exclamation-triangle-fill me-2"),
                html.Strong(f"Equity negativa all'anno {T}: "),
                (f"saldo residuo ({fe(remain_at_T)}) > ricavo di vendita "
                 f"({fe(prop_at_T * (1 - sell_cost_r))}). "
                 f"Perdita attesa: {fe(abs(net_terminal))}."),
            ], color="danger", className="mb-3 small"))

        sub_kpis = dbc.Row([
            dbc.Col(html.Div([
                html.Div("CF netto/mese", style={"fontSize": "0.68rem", "color": "#64748b"}),
                html.Div(f"{net_cf_mens:+,.0f}\u00a0\u20ac", style={
                    "fontSize": "1.25rem", "fontWeight": "700",
                    "color": "#10b981" if net_cf_mens >= 0 else "#ef4444",
                }),
            ], className="p-2 text-center rounded",
               style={"background": "#f8fafc", "border": "1px solid #e2e8f0"})),
            dbc.Col(html.Div([
                html.Div("Gross Yield", style={"fontSize": "0.68rem", "color": "#64748b"}),
                html.Div(fp(gross_yield), style={
                    "fontSize": "1.25rem", "fontWeight": "700", "color": "#3b82f6",
                }),
            ], className="p-2 text-center rounded",
               style={"background": "#f8fafc", "border": "1px solid #e2e8f0"})),
            dbc.Col(html.Div([
                html.Div("Cap Rate", style={"fontSize": "0.68rem", "color": "#64748b"}),
                html.Div(fp(cap_rate), style={
                    "fontSize": "1.25rem", "fontWeight": "700", "color": "#8b5cf6",
                }),
            ], className="p-2 text-center rounded",
               style={"background": "#f8fafc", "border": "1px solid #e2e8f0"})),
        ], className="mb-3 g-2")

        table_rows = [
            ("Affitto lordo mensile",          fe(affitto_lordo, 2)),
            ("Perdita da vacancy",              f"\u2212 {fe(vacancy_drag, 2)}"),
            ("Imposte sul canone",              f"\u2212 {fe(tax_mensile, 2)}"),
            ("Manutenzione ord. mensile",       f"\u2212 {fe(maint_ord_mens, 2)}"),
            ("Manutenzione straord. mensile",   f"\u2212 {fe(maint_ext_mens, 2)}"),
            ("Ricerca inquilino (mensil.)",     f"\u2212 {fe(ricerca_mens, 2)}"),
            ("Spese fisse mensili",             f"\u2212 {fe(spese_fisse_mens, 2)}"),
            ("IMU mensile",                     f"\u2212 {fe(imu_mens, 2)}"),
            ("Rata mutuo",                      f"\u2212 {fe(monthly_pmt_val, 2)}"),
            ("Cashflow netto mensile",          f"{'▲' if net_cf_mens >= 0 else '▼'} {fe(abs(net_cf_mens), 2)}"),
            ("\u2500", "\u2500"),
            ("Gross Rental Yield",              fp(gross_yield)),
            ("Cap Rate (pre-tax NOI/val.)",     fp(cap_rate)),
            ("Net Yield (post-tax NOI/val.)",   fp(net_yield)),
            ("Cash-on-Cash Return",             fp(coc_return)),
            (f"IRR (orizzonte {T} anni)",       irr_display),
            ("NPV totale",                      fe(npv_total)),
            ("Canone break-even",               fe(break_even_rent, 0) + " \u20ac/mese"),
        ]
        detail_table = dbc.Table(
            html.Tbody([
                html.Tr([html.Td(lbl, className="small"),
                         html.Td(val, className="small text-end fw-semibold")])
                for lbl, val in table_rows
            ]),
            size="sm", bordered=True, hover=True, responsive=True, className="mb-0",
        )

        return (
            html.Div(alerts + [hero_irr, sub_kpis, detail_table]),
            waterfall_fig, cum_fig, npv_fig, irr_fig,
        )
