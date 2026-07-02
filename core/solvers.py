"""Numerical / inverse solvers — depend only on core.finance."""
from __future__ import annotations

import numpy as np
from scipy.optimize import brentq

from .finance import build_costs, pmt


# ── internal helper ──────────────────────────────────────────────────────────

def _total_init(
    offerta, pct_anti, rendita, tipo, mediatore,
    notaio, perizia, ass_inc, ass_vita, donaz_cost, kiron_pct, med_pct,
) -> float:
    anticipo = offerta * pct_anti
    items, _ = build_costs(
        offerta, anticipo, rendita, tipo, mediatore,
        notaio, perizia, ass_inc, ass_vita, donaz_cost, kiron_pct, med_pct,
    )
    return items["TOTALE INIZIALE"]


# ── public solvers ───────────────────────────────────────────────────────────

def inv_home_from_budget(
    budget, pct_anti, rendita, tipo, mediatore,
    notaio, perizia, ass_inc, ass_vita, donaz_cost, kiron_pct, med_pct,
) -> float | None:
    """Max home price such that total initial cost ≤ *budget*."""
    def f(x):
        return (
            _total_init(x, pct_anti, rendita, tipo, mediatore,
                        notaio, perizia, ass_inc, ass_vita,
                        donaz_cost, kiron_pct, med_pct)
            - budget
        )
    try:
        if f(1_000) > 0:
            return None
        return brentq(f, 1_000, 50_000_000, xtol=0.5)
    except Exception:
        return None


def inv_home_from_payment(
    max_pmt: float, pct_anti: float, annual_rate: float, years: int,
) -> tuple[float, float]:
    """Max home price such that monthly payment ≤ *max_pmt*."""
    r = annual_rate / 12
    n = years * 12
    if annual_rate <= 0:
        mutuo = max_pmt * n
    else:
        mutuo = max_pmt * (1 - (1 + r) ** -n) / r
    offerta = mutuo / max(1 - pct_anti, 0.001)
    return offerta, mutuo


def inv_duration_from_payment(
    max_pmt: float, mutuo: float, annual_rate: float,
) -> int | None:
    """Minimum years so that monthly payment ≤ *max_pmt*."""
    if annual_rate <= 0:
        return int(np.ceil(mutuo / (max_pmt * 12)))
    r = annual_rate / 12
    ratio = 1 - mutuo * r / max_pmt
    if ratio <= 0:
        return None
    months = -np.log(ratio) / np.log(1 + r)
    return int(np.ceil(months / 12))


def inv_max_rate(max_pmt: float, mutuo: float, years: int) -> float | None:
    """Maximum annual rate such that monthly payment ≤ *max_pmt*."""
    def f(r):
        return pmt(mutuo, r, years) - max_pmt

    if f(0.0001) > 0:
        return None
    try:
        return brentq(f, 0.0001, 0.50)
    except Exception:
        return None


def inv_anticipo_from_budget(
    budget, offerta, rendita, tipo, mediatore,
    notaio, perizia, ass_inc, ass_vita, donaz_cost, kiron_pct, med_pct,
) -> float | None:
    """Minimum anticipo (fixed *offerta*) so that total initial cost ≤ *budget*."""
    def f(anticipo):
        items, _ = build_costs(
            offerta, anticipo, rendita, tipo, mediatore,
            notaio, perizia, ass_inc, ass_vita, donaz_cost, kiron_pct, med_pct,
        )
        return items["TOTALE INIZIALE"] - budget

    lo, hi = offerta * 0.01, offerta * 0.999
    try:
        if f(lo) > 0:
            return None
        if f(hi) < 0:
            return hi
        return brentq(f, lo, hi, xtol=0.5)
    except Exception:
        return None
