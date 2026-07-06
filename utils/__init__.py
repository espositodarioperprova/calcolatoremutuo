"""Formatting utilities — no Dash or UI dependencies."""
from __future__ import annotations

import numpy as np

from utils.i18n import t  # noqa: F401 — re-exported for convenience


def fe(v, dec: int = 0) -> str:
    """Format *v* as a euro string, e.g. ``€ 1.234,00``."""
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "N/D"
    return f"€\u202f{v:,.{dec}f}"


def fp(v, dec: int = 2) -> str:
    """Format *v* as a percentage string, e.g. ``3.20%``."""
    if v is None:
        return "N/D"
    return f"{v * 100:.{dec}f}%"
