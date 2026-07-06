"""Sidebar-level callbacks: slider sync, LTV indicator, advanced collapse."""
from __future__ import annotations

from dash import Input, Output, State, ctx, html

from utils.i18n import t


def register_sidebar_callbacks(app) -> None:
    @app.callback(
        Output("offerta-slider", "value"),
        Output("offerta", "value", allow_duplicate=True),
        Input("offerta", "value"),
        Input("offerta-slider", "value"),
        prevent_initial_call=True,
    )
    def sync_offerta(inp_val, slider_val):
        trigger = ctx.triggered_id
        if trigger == "offerta" and inp_val:
            return inp_val, inp_val
        if trigger == "offerta-slider" and slider_val:
            return slider_val, slider_val
        return inp_val or 100_000, inp_val or 100_000

    @app.callback(
        Output("ltv-display", "children"),
        Input("offerta", "value"),
        Input("anticipo", "value"),
    )
    def update_ltv(offerta, anticipo):
        if not offerta or not anticipo or offerta <= 0:
            return ""
        ltv = (offerta - anticipo) / offerta * 100
        pct_anti = anticipo / offerta * 100
        color = (
            "text-success" if ltv <= 80
            else "text-warning" if ltv <= 90
            else "text-danger"
        )
        return html.Span(
            f"Anticipo: {pct_anti:.1f}%  ·  LTV: {ltv:.1f}%",
            className=color,
        )

    @app.callback(
        Output("adv-collapse", "is_open"),
        Input("adv-toggle", "n_clicks"),
        State("adv-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_adv(n, is_open):
        return not is_open

    # ── Show "Costo atti donazione" only when tipo == prima_donaz ──────────
    @app.callback(
        Output("donaz-cost-section", "style"),
        Input("tipo", "value"),
    )
    def toggle_donaz_section(tipo):
        return {} if tipo == "prima_donaz" else {"display": "none"}

    # ── Disable optional inputs when their switch is off ───────────────────
    @app.callback(
        Output("ass-inc", "disabled"),
        Input("ass-inc-on", "value"),
    )
    def disable_ass_inc(on):
        return not bool(on)

    @app.callback(
        Output("ass-vita", "disabled"),
        Input("ass-vita-on", "value"),
    )
    def disable_ass_vita(on):
        return not bool(on)

    @app.callback(
        Output("donaz-cost", "disabled"),
        Input("donaz-cost-on", "value"),
    )
    def disable_donaz_cost(on):
        return not bool(on)

    # ── Translate sidebar labels on language change ────────────────────────
    @app.callback(
        Output("sb-hdr", "children"),
        Output("sb-lbl-offerta", "children"),
        Output("sb-ft-offerta", "children"),
        Output("sb-lbl-anticipo", "children"),
        Output("sb-lbl-durata", "children"),
        Output("sb-lbl-tasso", "children"),
        Output("sb-lbl-tipo", "children"),
        Output("tipo", "options"),
        Output("sb-ft-tipo", "children"),
        Output("sb-lbl-rendita", "children"),
        Output("sb-ft-rendita", "children"),
        Output("mediatore", "label"),
        Output("sb-adv-toggle-txt", "children"),
        Output("sb-lbl-notaio", "children"),
        Output("sb-ft-notaio", "children"),
        Output("sb-lbl-perizia", "children"),
        Output("sb-ft-perizia", "children"),
        Output("sb-lbl-ass-inc", "children"),
        Output("sb-ft-ass-inc", "children"),
        Output("sb-lbl-ass-vita", "children"),
        Output("sb-ft-ass-vita", "children"),
        Output("sb-lbl-donaz", "children"),
        Output("sb-ft-donaz", "children"),
        Output("sb-lbl-kiron", "children"),
        Output("sb-ft-kiron", "children"),
        Output("sb-lbl-med-pct", "children"),
        Output("sb-ft-med-pct", "children"),
        Input("lang-store", "data"),
    )
    def translate_sidebar(lang):
        return (
            t("sidebar.header", lang),
            t("sidebar.offerta.label", lang),
            t("sidebar.offerta.help", lang),
            t("sidebar.anticipo.label", lang),
            t("sidebar.durata.label", lang),
            t("sidebar.tasso.label", lang),
            t("sidebar.tipo.label", lang),
            [
                {"label": t("sidebar.tipo.prima", lang), "value": "prima"},
                {"label": t("sidebar.tipo.prima_donaz", lang), "value": "prima_donaz"},
                {"label": t("sidebar.tipo.seconda", lang), "value": "seconda"},
            ],
            t("sidebar.tipo.help", lang),
            t("sidebar.rendita.label", lang),
            t("sidebar.rendita.help", lang),
            t("sidebar.mediatore.label", lang),
            t("sidebar.adv_toggle", lang),
            t("sidebar.notaio.label", lang),
            t("sidebar.notaio.help", lang),
            t("sidebar.perizia.label", lang),
            t("sidebar.perizia.help", lang),
            t("sidebar.ass_inc.label", lang),
            t("sidebar.ass_inc.help", lang),
            t("sidebar.ass_vita.label", lang),
            t("sidebar.ass_vita.help", lang),
            t("sidebar.donaz.label", lang),
            t("sidebar.donaz.help", lang),
            t("sidebar.kiron.label", lang),
            t("sidebar.kiron.help", lang),
            t("sidebar.med_pct.label", lang),
            t("sidebar.med_pct.help", lang),
        )

    @app.callback(
        Output("kiron-pct", "disabled"),
        Input("kiron-on", "value"),
    )
    def disable_kiron(on):
        return not bool(on)

    # ── Enable canone-growth inputs when switch is on ──────────────────────
    @app.callback(
        Output("canone-growth-pct",  "disabled"),
        Output("canone-step-years",  "disabled"),
        Input("canone-disallacciato", "value"),
    )
    def toggle_canone_params(disallacciato):
        disabled = not bool(disallacciato)
        return disabled, disabled
