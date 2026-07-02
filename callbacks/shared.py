"""Shared constants and helpers used across all callback modules."""
from __future__ import annotations

from dash import Input

#: Full list of sidebar inputs; spread into every tab callback.
SIDEBAR_INPUTS: list[Input] = [
    Input("offerta", "value"),
    Input("anticipo", "value"),
    Input("durata", "value"),
    Input("tasso", "value"),
    Input("tipo", "value"),
    Input("rendita", "value"),
    Input("mediatore", "value"),
    Input("notaio", "value"),
    Input("perizia-val", "value"),
    Input("ass-inc", "value"),
    Input("ass-vita", "value"),
    Input("donaz-cost", "value"),
    Input("kiron-pct", "value"),
    Input("med-pct", "value"),
    # Optional-cost enable switches
    Input("ass-inc-on", "value"),
    Input("ass-vita-on", "value"),
    Input("donaz-cost-on", "value"),
    Input("kiron-on", "value"),
]


def _safe(v, default=0):
    """Return *v* if not ``None``, otherwise *default*."""
    return v if v is not None else default
