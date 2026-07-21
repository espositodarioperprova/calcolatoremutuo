"""Tab 2 — Valutazione Investimento: comprehensive buy-to-let ROI analysis."""
from __future__ import annotations

import numpy as np
from scipy.optimize import brentq
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import Output, Input, dcc, html
from utils.i18n import t

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
        Input("lang-store", "data"),
    )
    def update_rent(
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
        rendita_v = _safe(rendita, 206.58)
        notaio = _safe(notaio, 2000)
        perizia = _safe(perizia, 350)
        ass_inc = _safe(ass_inc,    1300) if ass_inc_on != False else 0.0
        ass_vita = _safe(ass_vita,   3500) if ass_vita_on != False else 0.0
        donaz_c = _safe(donaz_cost, 2500) if donaz_on != False else 0.0
        kiron = (_safe(kiron_pct, 2) / 100) if kiron_on != False else 0.0
        med_pct = _safe(med_pct, 4) / 100
        tipo = tipo or "prima_donaz"

        items, _ = build_costs(
            offerta, anticipo, rendita_v, tipo, bool(mediatore),
            notaio, perizia, ass_inc, ass_vita, donaz_c, kiron, med_pct,
        )
        costo_iniziale = items["TOTALE INIZIALE"]
        mutuo = max(offerta - anticipo, 0)
        monthly_pmt_v = pmt(mutuo, tasso_r, durata)

        default_affitto = max(int(offerta * 0.0054 / 10) * 10, 300)
        default_imu = 0.0 if tipo in ("prima", "prima_donaz") else 1.06
        imu_default_ann = rendita_v * 1.05 * 160 * default_imu / 100
        if imu_default_ann > 0:
            imu_text = t("rent.imu.formula", lang).format(
                aliq=default_imu, ann=fe(imu_default_ann, 0), mese=fe(imu_default_ann / 12, 1)
            )
        else:
            imu_text = t("rent.imu.prima_casa", lang)

        return html.Div([
            dbc.Row([
                # ── Left: inputs ──────────────────────────────────────────
                dbc.Col([
                    html.H5(t("rent.lbl.section_header", lang),
                            className="fw-bold mb-2"),

                    dbc.Row([
                        dbc.Col([
                            dbc.Label(t("rent.lbl.affitto", lang)),
                            dbc.Input(id="affitto", type="number",
                                      value=default_affitto, min=0, step=1),
                        ]),
                        dbc.Col([
                            dbc.Label(t("rent.lbl.regime", lang)),
                            dbc.Select(
                                id="regime-tassazione",
                                options=[
                                    {"label": t("rent.opt.cc10", lang),
                                     "value": "cc10"},
                                    {"label": t("rent.opt.cs21", lang),
                                     "value": "cs21"},
                                    {"label": t("rent.opt.irpef35",
                                                lang), "value": "irpef35"},
                                    {"label": t("rent.opt.irpef43",
                                                lang), "value": "irpef43"},
                                ],
                                value="cc10", className="form-select",
                            ),
                        ]),
                    ], className="mb-1"),

                    dbc.Row([
                        dbc.Col([
                            dbc.Label([
                                t("rent.lbl.discount", lang),
                                html.Span(" \u24d8", id="tooltip-discount-target",
                                          style={"cursor": "pointer", "color": "#64748b"}),
                            ]),
                            dbc.Tooltip(
                                html.Div([
                                    html.P(t("rent.tt.discount.title", lang),
                                           className="fw-semibold mb-1"),
                                    html.Ul([
                                        html.Li(
                                            t("rent.tt.discount.li1", lang)),
                                        html.Li(
                                            t("rent.tt.discount.li2", lang)),
                                        html.Li(
                                            t("rent.tt.discount.li3", lang)),
                                    ], className="mb-1 ps-3 small"),
                                    html.P(t("rent.tt.discount.footer", lang),
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
                            dbc.Label(t("rent.lbl.inflaz", lang)),
                            dbc.InputGroup([
                                dbc.Input(id="inflaz", type="number",
                                          value=2.0, min=0, max=20, step=0.1),
                                dbc.InputGroupText("%"),
                            ]),
                        ]),
                    ], className="mb-1"),



                    # ── 4-col: manutenzione + ricerca ─────────────────────
                    dbc.Row([
                        dbc.Col([
                            dbc.Label(t("rent.lbl.mant_straord", lang),
                                      className="small fw-semibold"),
                            dbc.InputGroup([
                                dbc.Input(id="manutenzione-freq", type="number",
                                          value=0.2, min=0, max=5, step=0.05),
                                dbc.InputGroupText("ev/a"),
                            ], size="sm"),
                        ], xs=6, md=3),
                        dbc.Col([
                            dbc.Label(t("rent.lbl.costo_evento", lang),
                                      className="small fw-semibold"),
                            dbc.InputGroup([
                                dbc.Input(id="manutenzione-costo", type="number",
                                          value=3000, min=0, step=50),
                                dbc.InputGroupText("\u20ac"),
                            ], size="sm"),
                        ], xs=6, md=3),
                        dbc.Col([
                            dbc.Label(t("rent.lbl.ricerca_inq", lang),
                                      className="small fw-semibold"),
                            dbc.InputGroup([
                                dbc.Input(id="ricerca-costo", type="number",
                                          value=500, min=0, step=10),
                                dbc.InputGroupText("\u20ac"),
                            ], size="sm"),
                        ], xs=6, md=3),
                        dbc.Col([
                            dbc.Label(t("rent.lbl.freq_ricerca", lang),
                                      className="small fw-semibold"),
                            dbc.InputGroup([
                                dbc.Input(id="ricerca-freq", type="number",
                                          value=0.5, min=0, max=5, step=0.1),
                                dbc.InputGroupText("ev/a"),
                            ], size="sm"),
                        ], xs=6, md=3),
                    ], className="mb-1 g-2"),

                    # ── 3-col: IMU + costi vendita + anno uscita ──────────
                    dbc.Row([
                        dbc.Col([
                            dbc.Label(t("rent.lbl.imu", lang),
                                      className="small fw-semibold"),
                            dbc.InputGroup([
                                dbc.Input(id="imu-rate", type="number",
                                          value=default_imu, min=0, max=3, step=0.01),
                                dbc.InputGroupText("%"),
                            ], size="sm"),
                            dbc.FormText(imu_text),
                        ], xs=12, md=4),
                        dbc.Col([
                            dbc.Label(t("rent.lbl.costi_vendita", lang),
                                      className="small fw-semibold"),
                            dbc.InputGroup([
                                dbc.Input(id="costo-vendita-pct", type="number",
                                          value=4.0, min=0, max=15, step=0.5),
                                dbc.InputGroupText("%"),
                            ], size="sm"),
                        ], xs=6, md=4),
                        dbc.Col([
                            dbc.Label(t("rent.lbl.anno_uscita", lang),
                                      className="small fw-semibold"),
                            dbc.InputGroup([
                                dbc.Input(id="anno-uscita", type="number",
                                          value=None,
                                          placeholder=f"default: {int(durata)}",
                                          min=1, max=999, step=1),
                                dbc.InputGroupText("a"),
                            ], size="sm"),
                        ], xs=6, md=4),
                    ], className="mb-1 g-2"),

                    # ── Crescita canone section ────────────────────────────
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col(
                                    html.Small(t("rent.lbl.crescita_canone", lang),
                                               className="fw-semibold text-muted"),
                                ),
                                dbc.Col(
                                    dbc.Switch(
                                        id="canone-disallacciato", value=False,
                                        label=t("rent.lbl.disallaccia", lang),
                                        className="mb-0",
                                    ),
                                    className="col-auto",
                                ),
                            ], className="align-items-center mb-2"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label(t("rent.lbl.crescita_pct", lang),
                                              className="small"),
                                    dbc.InputGroup([
                                        dbc.Input(id="canone-growth-pct", type="number",
                                                  value=2.0, min=0, max=20, step=0.1,
                                                  disabled=True),
                                        dbc.InputGroupText("%"),
                                    ]),
                                ]),
                                dbc.Col([
                                    dbc.Label(t("rent.lbl.adeguamento", lang),
                                              className="small"),
                                    dbc.InputGroup([
                                        dbc.Input(id="canone-step-years", type="number",
                                                  value=5, min=1, max=10, step=1,
                                                  disabled=True),
                                        dbc.InputGroupText("anni"),
                                    ]),
                                ]),
                            ]),
                        ], className="py-2"),
                    ], className="mb-2 border", style={"borderRadius": "8px"}),

                ]),

                # ── Right: waterfall chart fixed 300×300 ───────────────────────────
                dbc.Col([
                    dcc.Graph(id="waterfall-chart",
                              config={"displayModeBar": False,
                                      "responsive": False},
                              style={"height": "400px", "width": "500px"}),
                ], className="col-auto"),
            ]),

            html.Div(id="investment-results", className="mt-3"),

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
        Input("lang-store",         "data"),
    )
    def update_investment(
        affitto, regime, discount, inflaz,
        maint_freq, maint_costo, imu_rate_input,
        costo_vendita_pct,
        anno_uscita,
        canone_disallacciato, canone_growth_pct, canone_step_years,
        ricerca_costo, ricerca_freq,
        store, lang,
    ):
        _empty = go.Figure().update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        if not store or not affitto:
            return "", _empty, _empty, _empty, _empty

        # ── Unpack store ───────────────────────────────────────────────────
        offerta = store["offerta"]
        mutuo_val = store["mutuo"]
        costo_iniziale = store["costo_iniziale"]
        monthly_pmt_val = store["monthly_pmt"]
        durata = store["durata"]
        rendita_val = store.get("rendita", 206.58)
        tipo = store.get("tipo", "prima_donaz")
        tasso_r = store.get("tasso_r", 0.032)

        # ── Parameters ────────────────────────────────────────────────────
        affitto_lordo = _safe(affitto, 800)
        tax_r = _TAX.get(regime or "cs21", _TAX["cs21"])
        discount_r = _safe(discount, 5) / 100
        inflaz_r = _safe(inflaz, 2) / 100
        vacancy_r = 0.0
        spese_fisse_ann = 0.0
        maint_ord_r = 0.0
        maint_freq_v = _safe(maint_freq, 0.2)
        maint_costo_v = _safe(maint_costo, 3000)
        imu_r = _safe(imu_rate_input, 0.0 if tipo == "prima" else 0.96) / 100
        sell_cost_r = _safe(costo_vendita_pct, 4) / 100
        ricerca_mens = _safe(ricerca_costo, 500) * \
            _safe(ricerca_freq, 0.5) / 12

        # Anno di uscita
        T = max(int(_safe(anno_uscita, None) or durata), 1)

        # Canone growth parameters
        if canone_disallacciato:
            canone_growth_ann = _safe(canone_growth_pct, 2.0) / 100
            step_yrs = max(int(_safe(canone_step_years, 2)), 1)
        else:
            canone_growth_ann = inflaz_r
            step_yrs = 1

        # ── Base monthly components ────────────────────────────────────────
        affitto_eff = affitto_lordo * (1 - vacancy_r)
        vacancy_drag = affitto_lordo - affitto_eff
        tax_mensile = affitto_eff * tax_r
        affitto_netto = affitto_eff - tax_mensile

        imu_ann = rendita_val * 1.05 * 160 * imu_r
        imu_mens = imu_ann / 12
        maint_ord_mens = (offerta * maint_ord_r) / 12
        maint_ext_mens = (maint_freq_v * maint_costo_v) / 12
        spese_fisse_mens = spese_fisse_ann / 12
        costi_op_base = (imu_mens + maint_ord_mens + maint_ext_mens
                         + spese_fisse_mens + ricerca_mens)

        net_cf_mens = affitto_netto - monthly_pmt_val - costi_op_base

        # ── Base KPI figures ───────────────────────────────────────────────
        aff_lordo_ann = affitto_lordo * 12
        aff_eff_ann = affitto_eff * 12
        aff_netto_ann = affitto_netto * 12
        costi_op_ann = costi_op_base * 12
        gross_yield = aff_lordo_ann / offerta
        noi_pretax = aff_eff_ann - costi_op_ann
        cap_rate = noi_pretax / offerta
        noi_posttax = aff_netto_ann - costi_op_ann
        net_yield = noi_posttax / offerta
        net_cf_ann = net_cf_mens * 12
        coc_return = net_cf_ann / costo_iniziale
        denom = max((1 - vacancy_r) * (1 - tax_r), 1e-6)
        break_even_rent = (monthly_pmt_val + costi_op_base) / denom

        # ── Monthly CF series over T years ─────────────────────────────────
        n_months_T = T * 12
        r_inf_m = (1 + inflaz_r) ** (1 / 12) - 1
        r_disc_m = (1 + discount_r) ** (1 / 12) - 1
        durata_months = int(durata) * 12

        cfs = []
        for m in range(1, n_months_T + 1):
            yr_0 = (m - 1) // 12
            if canone_disallacciato:
                n_steps = yr_0 // step_yrs
                rent_growth = (1 + canone_growth_ann) ** (n_steps * step_yrs)
            else:
                rent_growth = (1 + r_inf_m) ** (m - 1)

            net_rent_m = affitto_eff * rent_growth * (1 - tax_r)
            ops_m = costi_op_base * (1 + r_inf_m) ** (m - 1)
            mort_m = monthly_pmt_val if m <= durata_months else 0.0
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
        prop_at_T = offerta * (1 + inflaz_r) ** T
        remain_at_T = _remaining(T * 12)
        net_terminal = prop_at_T * (1 - sell_cost_r) - remain_at_T
        underwater = net_terminal < 0 and T < int(durata)

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
        dv = (1 + r_disc_m) ** np.arange(1, n_months_T + 1)
        npv_total = (-costo_iniziale
                     + float(np.sum(cfs_arr / dv))
                     + net_terminal / (1 + r_disc_m) ** n_months_T)

        # ── Chart 1: Waterfall ─────────────────────────────────────────────
        wf_x = [t("rent.wf.affitto_lordo", lang), t(
            "rent.wf.imposte", lang), t("rent.wf.manutenzione", lang)]
        wf_y = [affitto_lordo, -tax_mensile, -maint_ext_mens]
        wf_m = ["absolute", "relative", "relative"]

        if imu_mens > 0.01:
            wf_x.append(t("rent.wf.imu", lang))
            wf_y.append(-imu_mens)
            wf_m.append("relative")
        if ricerca_mens > 0.01:
            wf_x.append(t("rent.wf.ricerca_inq", lang))
            wf_y.append(-ricerca_mens)
            wf_m.append("relative")
        wf_x.append(t("rent.wf.rata_mutuo", lang))
        wf_y.append(-monthly_pmt_val)
        wf_m.append("relative")
        wf_x.append(t("rent.wf.cf_netto", lang))
        wf_y.append(net_cf_mens)
        wf_m.append("total")

        waterfall_fig = go.Figure(go.Waterfall(
            orientation="v", measure=wf_m, x=wf_x, y=wf_y,
            connector={"line": {"color": "#cbd5e1"}},
            increasing={"marker": {"color": "#10b981"}},
            decreasing={"marker": {"color": "#ef4444"}},
            totals={"marker": {
                "color": "#3b82f6" if net_cf_mens >= 0 else "#ef4444"}},
            texttemplate="%{y:,.0f} \u20ac", textposition="outside",
        ))
        waterfall_fig.update_layout(
            title=t("rent.wf.title", lang).format(
                affitto=fe(affitto_lordo, 0)),
            height=400, width=500, autosize=False, margin=dict(t=50, b=40, l=50, r=20), showlegend=False,
        )

        # ── Chart 2: Cumulative P&L ────────────────────────────────────────
        years = list(range(0, T + 1))
        cum_cf = 0.0
        cum_cfs_yr = []
        equity_gain = []
        total_pnl = []

        for yr in years:
            if yr > 0:
                cum_cf += sum(cfs[(yr - 1) * 12: yr * 12])
            prop_val_yr = offerta * (1 + inflaz_r) ** yr
            remaining_yr = _remaining(yr * 12)
            net_equity_yr = prop_val_yr - remaining_yr - costo_iniziale
            cum_cfs_yr.append(cum_cf)
            equity_gain.append(net_equity_yr)
            total_pnl.append(cum_cf + net_equity_yr)

        cum_fig = go.Figure()
        cum_fig.add_trace(go.Scatter(x=years, y=cum_cfs_yr, name=t("rent.cum.cf_operativi", lang),
                                     mode="lines", line=dict(color="#3b82f6", width=2)))
        cum_fig.add_trace(go.Scatter(x=years, y=equity_gain, name=t("rent.cum.equity_gain", lang),
                                     mode="lines", line=dict(color="#10b981", width=2)))
        cum_fig.add_trace(go.Scatter(x=years, y=total_pnl, name=t("rent.cum.pnl_totale", lang),
                                     mode="lines+markers", line=dict(color="#f59e0b", width=2.5), marker=dict(size=5)))
        cum_fig.add_hline(y=0, line_dash="dot",
                          line_color="#94a3b8", annotation_text=t("rent.cum.breakeven", lang))
        if T != int(durata):
            cum_fig.add_vline(x=T, line_dash="dash", line_color="#ef4444",
                              annotation_text=t("rent.cum.uscita", lang).format(T=T))
        cum_fig.update_layout(
            title=t("rent.cum.title", lang).format(T=T),
            xaxis_title=t("rent.cum.xaxis", lang), yaxis_title=t("rent.cum.yaxis", lang), height=380,
            margin=dict(t=50, b=40, l=60, r=20),
            legend=dict(orientation="h", yanchor="bottom",
                        y=1.02, xanchor="right", x=1),
        )

        # ── Chart 3: NPV vs appreciation ──────────────────────────────────
        apprezz_range = np.linspace(-0.02, 0.07, 30)
        npv_range = []
        for inf in apprezz_range:
            term_i = offerta * (1 + inf) ** T * \
                (1 - sell_cost_r) - _remaining(T * 12)
            npv_i = (-costo_iniziale
                     + float(np.sum(cfs_arr / dv))
                     + term_i / (1 + r_disc_m) ** n_months_T)
            npv_range.append(npv_i)

        npv_fig = go.Figure()
        npv_fig.add_trace(go.Scatter(x=apprezz_range * 100, y=npv_range,
                                     mode="lines", line=dict(color="#8b5cf6", width=2.5),
                                     fill="tozeroy", fillcolor="rgba(139,92,246,0.12)"))
        npv_fig.add_hline(y=0, line_dash="dot", line_color="#94a3b8")
        npv_fig.add_vline(x=inflaz_r * 100, line_dash="dash",
                          annotation_text=t("rent.npv.vline", lang).format(val=fp(inflaz_r)))
        npv_fig.update_layout(
            title=t("rent.npv.title", lang).format(disc=fp(discount_r), T=T),
            xaxis_title=t("rent.npv.xaxis", lang), yaxis_title=t("rent.npv.yaxis", lang),
            height=380, margin=dict(t=50, b=40, l=60, r=20),
        )

        # ── Chart 4: IRR vs rent level — consistent with hero IRR ──────────────────
        # Pre-compute time-invariant arrays so the per-rent loop is fast.
        _m_arr = np.arange(1, n_months_T + 1)
        _ops_arr = costi_op_base * (1 + r_inf_m) ** (_m_arr - 1)
        _mort_arr = np.where(_m_arr <= durata_months, monthly_pmt_val, 0.0)
        if canone_disallacciato:
            _yr0_arr = (_m_arr - 1) // 12
            _nsteps_arr = _yr0_arr // step_yrs
            _growth_arr = (1 + canone_growth_ann) ** (_nsteps_arr * step_yrs)
        else:
            _growth_arr = (1 + r_inf_m) ** (_m_arr - 1)

        rent_range = np.linspace(
            max(affitto_lordo * 0.5, 200), affitto_lordo * 2, 25)
        irr_range = []
        for rent in rent_range:
            _eff = rent * (1 - vacancy_r)
            _cfs_r = _eff * _growth_arr * (1 - tax_r) - _mort_arr - _ops_arr

            def _npv_r(r_m: float, _c: np.ndarray = _cfs_r) -> float:
                if r_m <= -1.0:
                    return float("inf")
                dv2 = (1 + r_m) ** _m_arr
                return (-costo_iniziale
                        + float(np.sum(_c / dv2))
                        + net_terminal / (1 + r_m) ** n_months_T)
            try:
                rm = brentq(_npv_r, -0.09 / 12, 0.5 / 12, maxiter=200)
                irr_range.append((1 + rm) ** 12 - 1)
            except Exception:
                irr_range.append(None)

        irr_valid = [(r, v)
                     for r, v in zip(rent_range, irr_range) if v is not None]
        irr_fig = go.Figure()
        if irr_valid:
            rx, ry = zip(*irr_valid)
            irr_fig.add_trace(go.Scatter(x=list(rx), y=[v * 100 for v in ry],
                                         mode="lines", line=dict(color="#06b6d4", width=2.5),
                                         fill="tozeroy", fillcolor="rgba(6,182,212,0.12)"))
        irr_fig.add_hline(y=0, line_dash="dot", line_color="#94a3b8")
        irr_fig.add_vline(x=affitto_lordo, line_dash="dash",
                          annotation_text=t("rent.irr_chart.vline", lang).format(val=fe(affitto_lordo, 0)))
        irr_fig.update_layout(
            title=t("rent.irr_chart.title", lang).format(T=T),
            xaxis_title=t("rent.irr_chart.xaxis", lang), yaxis_title=t("rent.irr_chart.yaxis", lang),
            height=340, margin=dict(t=50, b=40, l=60, r=20),
        )

        # ── Hero IRR ──────────────────────────────────────────────────────
        if irr_ann is not None:
            irr_vs_btp = irr_ann - _BTP_REF
            sign = "+" if irr_vs_btp >= 0 else ""
            irr_color = "#10b981" if irr_ann >= discount_r else "#ef4444"
            irr_badge = t("rent.hero.vs_btp", lang).format(
                sign=sign, pp=irr_vs_btp * 100)
            irr_display = f"{irr_ann * 100:.2f}%"
            verdict = (t("rent.hero.verdict_ok", lang)
                       if irr_ann >= discount_r
                       else t("rent.hero.verdict_ko", lang))
        else:
            irr_color = "#94a3b8"
            irr_badge = "n/d"
            irr_display = "n/d"
            verdict = t("rent.hero.verdict_nd", lang)

        hero_irr = html.Div([
            html.Div(t("rent.hero.irr_label", lang), style={
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
                html.Span(t("rent.hero.orizzonte", lang),
                          style={"color": "#94a3b8"}),
                html.Span(f"{T} anni", className="fw-semibold"),
                html.Span(t("rent.hero.npv_label", lang),
                          style={"color": "#94a3b8"}),
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
                html.Strong(
                    t("rent.alert.equity_neg_title", lang).format(T=T)),
                t("rent.alert.equity_neg_body", lang).format(
                    saldo=fe(remain_at_T), ricavo=fe(prop_at_T * (1 - sell_cost_r)), perdita=fe(abs(net_terminal))
                ),
            ], color="danger", className="mb-3 small"))

        sub_kpis = dbc.Row([
            dbc.Col(html.Div([
                html.Div(t("rent.kpi.cf_netto_mese", lang),
                         style={"fontSize": "0.68rem", "color": "#64748b"}),
                html.Div(f"{net_cf_mens:+,.0f}\u00a0\u20ac", style={
                    "fontSize": "1.25rem", "fontWeight": "700",
                    "color": "#10b981" if net_cf_mens >= 0 else "#ef4444",
                }),
            ], className="p-2 text-center rounded",
                style={"background": "#f8fafc", "border": "1px solid #e2e8f0"})),
            dbc.Col(html.Div([
                html.Div(t("rent.kpi.gross_yield", lang), style={
                         "fontSize": "0.68rem", "color": "#64748b"}),
                html.Div(fp(gross_yield), style={
                    "fontSize": "1.25rem", "fontWeight": "700", "color": "#3b82f6",
                }),
            ], className="p-2 text-center rounded",
                style={"background": "#f8fafc", "border": "1px solid #e2e8f0"})),
            dbc.Col(html.Div([
                html.Div(t("rent.kpi.cap_rate", lang), style={
                         "fontSize": "0.68rem", "color": "#64748b"}),
                html.Div(fp(cap_rate), style={
                    "fontSize": "1.25rem", "fontWeight": "700", "color": "#8b5cf6",
                }),
            ], className="p-2 text-center rounded",
                style={"background": "#f8fafc", "border": "1px solid #e2e8f0"})),
        ], className="mb-3 g-2")

        table_rows = [
            (t("rent.tbl.affitto_lordo", lang),  fe(affitto_lordo, 2)),
            (t("rent.tbl.imposte", lang),
             f"\u2212 {fe(tax_mensile, 2)}"),
            (t("rent.tbl.manutenzione", lang),
             f"\u2212 {fe(maint_ext_mens, 2)}"),
            (t("rent.tbl.ricerca", lang),
             f"\u2212 {fe(ricerca_mens, 2)}"),
            (t("rent.tbl.imu", lang),            f"\u2212 {fe(imu_mens, 2)}"),
            (t("rent.tbl.rata", lang),
             f"\u2212 {fe(monthly_pmt_val, 2)}"),
            (t("rent.tbl.cf_netto", lang),
             f"{'▲' if net_cf_mens >= 0 else '▼'} {fe(abs(net_cf_mens), 2)}"),
            ("\u2500", "\u2500"),
            (t("rent.tbl.gross_yield", lang), fp(gross_yield)),
            (t("rent.tbl.cap_rate", lang),    fp(cap_rate)),
            (t("rent.tbl.net_yield", lang),   fp(net_yield)),
            (t("rent.tbl.coc", lang),         fp(coc_return)),
            (t("rent.tbl.irr", lang).format(T=T), irr_display),
            (t("rent.tbl.npv", lang),         fe(npv_total)),
            (t("rent.tbl.breakeven", lang),   fe(break_even_rent, 0) +
             " " + t("rent.tbl.euro_mese", lang)),
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
