"""Pure financial math — no Dash or UI dependencies."""
from __future__ import annotations

import numpy as np
import pandas as pd


def pmt(principal: float, annual_rate: float, years: int) -> float:
    """Monthly mortgage payment (rata mensile)."""
    if principal <= 0 or years <= 0:
        return 0.0
    if annual_rate <= 0:
        return principal / (years * 12)
    r = annual_rate / 12
    n = years * 12
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)


def valore_catastale(rendita: float, prima_casa: bool) -> float:
    """
    Valore catastale = rendita catastale × 1.05 × coefficiente.

    Prima casa : coeff 110 (imposta di registro 2 %).
    Non prima  : coeff 126 (imposta di registro 9 %).
    """
    return rendita * 1.05 * (110 if prima_casa else 126)


def build_costs(
    offerta: float,
    anticipo: float,
    rendita: float,
    tipo: str = "prima",          # "prima" | "prima_donaz" | "seconda"
    mediatore: bool = True,
    notaio: float = 2_000,
    perizia: float = 350,
    ass_inc: float = 1_300,
    ass_vita: float = 3_500,
    donaz_cost: float = 2_500,
    kiron_pct: float = 0.02,
    med_pct: float = 0.04,
) -> tuple[dict, float]:
    """Return itemised cost dict and valore catastale."""
    mutuo = max(offerta - anticipo, 0.0)
    prima = tipo in ("prima", "prima_donaz")
    val_cat = valore_catastale(rendita, prima)

    imp_sost = mutuo * (0.0025 if prima else 0.02)
    imp_reg = val_cat * (0.02 if prima else 0.09)
    quota_med = min(offerta * med_pct, 5_000) * 1.22 if mediatore else 0.0
    donaz = donaz_cost if tipo == "prima_donaz" else 0.0

    items: dict[str, float] = {
        "Anticipo": anticipo,
        "Commissione bancaria (1% mutuo)": mutuo * 0.01,
        "Imposta sostitutiva ipotecaria": imp_sost,
        "Spese istruttoria (mediatore creditizio)": mutuo * kiron_pct,
        "Perizia immobile": perizia,
        "Assicurazione incendio e scoppio": ass_inc,
        "Assicurazione vita": ass_vita,
        "Imposta di registro": imp_reg,
        "Provvigione agenzia immobiliare": quota_med,
        "Notaio": notaio,
        "Costo atti donazione": donaz,
    }
    items["TOTALE INIZIALE"] = sum(items.values())
    return items, val_cat


def amortization_schedule(
    principal: float, annual_rate: float, years: int
) -> pd.DataFrame:
    """Full monthly amortization schedule as a DataFrame."""
    if principal <= 0 or years <= 0:
        return pd.DataFrame()
    r = annual_rate / 12
    n = years * 12
    payment = pmt(principal, annual_rate, years)
    balance = principal
    rows = []
    for m in range(1, n + 1):
        interest = balance * r
        capital = payment - interest
        balance = max(balance - capital, 0.0)
        rows.append(
            {
                "Mese": m,
                "Anno": (m - 1) // 12 + 1,
                "Rata (€)": round(payment, 2),
                "Interessi (€)": round(interest, 2),
                "Capitale (€)": round(capital, 2),
                "Saldo residuo (€)": round(balance, 2),
            }
        )
    return pd.DataFrame(rows)
