"""Sidebar-level callbacks: slider sync, LTV indicator, advanced collapse."""
from __future__ import annotations

from dash import Input, Output, State, ctx, html


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
