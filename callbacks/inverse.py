"""Tab 2 — Cosa posso permettermi?: inverse calculator grids."""
from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import Output, Input, html, dash_table

from core.finance import pmt, build_costs
from core.solvers import (
    inv_home_from_budget,
    inv_home_from_payment,
    inv_duration_from_payment,
    inv_max_rate,
)
from utils import fe, fp
from .shared import SIDEBAR_INPUTS, _safe

_DT_CELL = {"textAlign": "center",
            "padding": "6px 10px", "fontFamily": "inherit"}
_DT_HEAD = {"fontWeight": "bold",
            "backgroundColor": "#f8fafc", "textAlign": "center"}


def register_inverse(app) -> None:
    @app.callback(
        Output("tab-inverse-content", "children"),
        *SIDEBAR_INPUTS,
        Input("spotlight-budget", "value"),
        Input("spotlight-pct-ref", "value"),
    )
    def update_inverse(
        offerta, anticipo, durata, tasso, tipo, rendita,
        mediatore, notaio, perizia, ass_inc, ass_vita,
        donaz_cost, kiron_pct, med_pct,
        spotlight_budget, spotlight_pct_ref,
        ass_inc_on, ass_vita_on, donaz_on, kiron_on,
    ):
        tasso_r = _safe(tasso, 3.2) / 100
        rendita = _safe(rendita, 206.58)
        durata = _safe(durata, 30)
        offerta = _safe(offerta, 100_000)
        anticipo = _safe(anticipo, 20_000)
        notaio = _safe(notaio, 2000)
        perizia = _safe(perizia, 350)
        ass_inc   = _safe(ass_inc,    1300) if ass_inc_on  != False else 0.0
        ass_vita  = _safe(ass_vita,   3500) if ass_vita_on != False else 0.0
        donaz_cost = _safe(donaz_cost, 2500) if donaz_on   != False else 0.0
        kiron_pct = (_safe(kiron_pct,  2) / 100) if kiron_on != False else 0.0
        med_pct = _safe(med_pct, 4) / 100
        tipo = tipo or "prima"
        pct_anti = anticipo / offerta if offerta > 0 else 0.20

        cost_kw = dict(
            rendita=rendita, tipo=tipo, mediatore=bool(mediatore),
            notaio=notaio, perizia=perizia, ass_inc=ass_inc, ass_vita=ass_vita,
            donaz_cost=donaz_cost, kiron_pct=kiron_pct, med_pct=med_pct,
        )

        # ── A: budget → max home ───────────────────────────────────────────
        budgets = [30_000, 40_000, 50_000, 75_000, 100_000]
        pcts = [0.10, 0.15, 0.20, 0.25, 0.30]
        grid = []
        for p in pcts:
            row = {"% Anticipo": fp(p, 0)}
            for b in budgets:
                res = inv_home_from_budget(b, p, **cost_kw)
                row[fe(b, 0)] = fe(res) if res else "—"
            grid.append(row)

        grid_table = dash_table.DataTable(
            data=grid,
            columns=[{"name": c, "id": c} for c in grid[0].keys()],
            style_cell=_DT_CELL, style_header=_DT_HEAD,
            style_data_conditional=[
                {"if": {"column_id": "% Anticipo"}, "fontWeight": "bold"}],
            style_table={"overflowX": "auto"},
        )

        # ── B: payment → max home ──────────────────────────────────────────
        payments = [300, 500, 700, 1000, 1500, 2000]
        pcts_b = [0.10, 0.20, 0.30]
        grid_b = []
        for p in pcts_b:
            row = {"% Anticipo": fp(p, 0)}
            for pm in payments:
                res_h, _ = inv_home_from_payment(pm, p, tasso_r, durata)
                row[f"Rata \u2264 {fe(pm, 0)}"] = fe(res_h)
            grid_b.append(row)

        table_b = dash_table.DataTable(
            data=grid_b,
            columns=[{"name": c, "id": c} for c in grid_b[0].keys()],
            style_cell=_DT_CELL, style_header=_DT_HEAD,
            style_data_conditional=[
                {"if": {"column_id": "% Anticipo"}, "fontWeight": "bold"}],
            style_table={"overflowX": "auto"},
        )

        # ── Spotlight: configurable budget & anticipo % ───────────────────
        budget_q = _safe(spotlight_budget, 50_000)
        pct_q = _safe(spotlight_pct_ref, 20) / 100
        home_q = inv_home_from_budget(budget_q, pct_q, **cost_kw)
        if home_q:
            items_q, _ = build_costs(
                home_q, home_q * pct_q, rendita, tipo, bool(mediatore),
                notaio, perizia, ass_inc, ass_vita, donaz_cost, kiron_pct, med_pct,
            )
            monthly_q = pmt(home_q * (1 - pct_q), tasso_r, durata)
            spotlight = dbc.Alert([
                html.H5(
                    f"🎯 Con {fe(budget_q)} cash e anticipo {fp(pct_q, 0)}",
                    className="alert-heading fw-bold",
                ),
                html.Hr(),
                dbc.Row([
                    dbc.Col([
                        html.H3(fe(home_q), className="text-success fw-bold"),
                        html.P("Valore massimo dell'immobile"),
                        html.P([html.Strong("Anticipo: "), fe(home_q * pct_q)]),
                        html.P([html.Strong("Mutuo: "),
                               fe(home_q * (1 - pct_q))]),
                        html.P([html.Strong("Rata mensile: "),
                               fe(monthly_q, 2), " / mese"]),
                    ], md=6),
                    dbc.Col([
                        html.H6("Come si distribuisce il budget:"),
                        dbc.Table(html.Tbody([
                            html.Tr([
                                html.Td(k, className="small"),
                                html.Td(fe(v, 0), className="small text-end"),
                            ])
                            for k, v in items_q.items() if v > 0
                        ]), size="sm", bordered=True),
                    ], md=6),
                ]),
            ], color="success")
        else:
            spotlight = dbc.Alert(
                "Con questi parametri il budget non è sufficiente.", color="danger")

        # ── C: duration needed ─────────────────────────────────────────────
        targets = [50_000, 100_000, 150_000, 200_000, 300_000, 500_000]
        pmts_d = [500, 700, 1000, 1500]
        grid_d = []
        for target in targets:
            mut = target * (1 - pct_anti)
            row = {"Prezzo immobile": fe(target), "Mutuo": fe(mut)}
            for pm in pmts_d:
                yrs = inv_duration_from_payment(pm, mut, tasso_r)
                row[f"Rata \u2264 {fe(pm, 0)}"] = (
                    f"{yrs} anni" if yrs and yrs <= 40 else "Imp."
                )
            grid_d.append(row)

        table_d = dash_table.DataTable(
            data=grid_d,
            columns=[{"name": c, "id": c} for c in grid_d[0].keys()],
            style_cell=_DT_CELL, style_header=_DT_HEAD,
            style_data_conditional=[
                {"if": {"column_id": "Prezzo immobile"}, "fontWeight": "bold"}],
            style_table={"overflowX": "auto"},
        )

        # ── D: max rate ────────────────────────────────────────────────────
        pmts_e = [400, 600, 800, 1000, 1200, 1500]
        mutui_e = [80_000, 120_000, 150_000, 200_000, 300_000]
        grid_e = []
        for pm in pmts_e:
            row = {"Rata max": fe(pm, 0)}
            for mut in mutui_e:
                r = inv_max_rate(pm, mut, durata)
                row[f"Mutuo {fe(mut, 0)}"] = fp(r) if r else "Imp."
            grid_e.append(row)

        table_e = dash_table.DataTable(
            data=grid_e,
            columns=[{"name": c, "id": c} for c in grid_e[0].keys()],
            style_cell=_DT_CELL, style_header=_DT_HEAD,
            style_data_conditional=[
                {"if": {"column_id": "Rata max"}, "fontWeight": "bold"}],
            style_table={"overflowX": "auto"},
        )

        return html.Div([
            spotlight, html.Hr(),
            html.H5("💶 A. Quanto posso comprare dato il mio budget cash?",
                    className="fw-bold mt-3 mb-1"),
            html.P(
                f"Tasso {fp(tasso_r)} · Durata {durata} anni — ogni cella = prezzo max immobile acquistabile",
                className="text-muted small mb-2",
            ),
            grid_table, html.Hr(),
            html.H5("💳 B. Quanto posso comprare data la rata mensile massima?",
                    className="fw-bold mt-3 mb-1"),
            html.P(
                f"Tasso {fp(tasso_r)} · Durata {durata} anni — ogni cella = prezzo max immobile",
                className="text-muted small mb-2",
            ),
            table_b, html.Hr(),
            html.H5("⏱️ C. Di quanti anni ho bisogno per sostenere una certa rata?",
                    className="fw-bold mt-3 mb-1"),
            html.P(
                f"Tasso {fp(tasso_r)} · Anticipo {fp(pct_anti)} — ogni cella = durata minima in anni",
                className="text-muted small mb-2",
            ),
            table_d, html.Hr(),
            html.H5("📉 D. Qual è il tasso massimo che posso sopportare?",
                    className="fw-bold mt-3 mb-1"),
            html.P(
                f"Durata {durata} anni — ogni cella = tasso annuo massimo sostenibile",
                className="text-muted small mb-2",
            ),
            table_e,
        ])
