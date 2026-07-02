"""Reusable Dash UI components."""
from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import html


def kpi_card(
    label: str,
    value: str,
    sub: str | None = None,
    color: str = "primary",
    icon: str = "",
) -> dbc.Card:
    """Gradient KPI card with hover lift effect.

    *color* maps to a CSS class ``kpi-card-{color}`` defined in custom.css.
    Valid values: ``primary``, ``danger``, ``warning``, ``secondary``, ``success``.
    """
    return dbc.Card(
        dbc.CardBody([
            html.P(
                [icon + ("  " if icon else ""), label],
                className="kpi-label",
            ),
            html.Div(value, className="kpi-value"),
            html.P(sub or "\u00a0", className="kpi-sub mb-0"),
        ]),
        className=f"kpi-card kpi-card-{color} shadow-lg h-100",
    )


def result_badge(label: str, value: str, ok: bool = True) -> dbc.Badge:
    """Coloured pill badge for pass/fail result indicators."""
    return dbc.Badge(
        f"{label}: {value}",
        color="success" if ok else "danger",
        pill=True,
        className="fs-6 px-3 py-2",
    )


def info_alert(text: str, color: str = "info") -> dbc.Alert:
    """Compact informational alert strip."""
    return dbc.Alert(text, color=color, className="small py-2 mb-2")
