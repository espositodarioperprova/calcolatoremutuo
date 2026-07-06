"""
Internationalisation (i18n) — Italian / English string catalogue.

Usage::

    from utils.i18n import t
    label = t("sidebar.offerta.label", lang)   # lang = "it" | "en"
"""
from __future__ import annotations

_T: dict[str, dict[str, str]] = {
    # ── Italian (default) ─────────────────────────────────────────────────────
    "it": {
        # ── App-level ──────────────────────────────────────────────────────────
        "app.title": "Simulatore acquisto con Mutuo per rendita",
        "app.subtitle": (
            "Analisi per l'acquisto di un immobile in Italia, a mezzo mutuo"
            " e con fini di rendita da locazione."
        ),
        "app.footer": "Calcolatore Mutuo per Rendita · Tutti i diritti riservati",
        "app.theme_toggle": "Attiva/disattiva dark mode",
        "app.lang_toggle": "Cambia lingua",
        "app.visits": "{n} visite",

        # ── Sidebar ────────────────────────────────────────────────────────────
        "sidebar.header": "Parametri",
        "sidebar.offerta.label": "Prezzo immobile (€)",
        "sidebar.offerta.help": (
            "Prezzo concordato con il venditore. Usa il cursore o digita il valore."
        ),
        "sidebar.anticipo.label": "Anticipo (€)",
        "sidebar.durata.label": "Durata (anni)",
        "sidebar.tasso.label": "Tasso annuo",
        "sidebar.tipo.label": "Tipo di acquisto",
        "sidebar.tipo.prima": "Prima casa",
        "sidebar.tipo.prima_donaz": "1a casa (se prima dono l'altra)",
        "sidebar.tipo.seconda": "Seconda casa / Non prima casa",
        "sidebar.tipo.help": (
            "Determina aliquota imposta di registro (2% / 9%)"
            " e diritto all'esenzione IMU."
        ),
        "sidebar.rendita.label": "Rendita catastale base (€)",
        "sidebar.rendita.help": "Dalla visura catastale dell'immobile",
        "sidebar.mediatore.label": "Includi provvigione agenzia",
        "sidebar.adv_toggle": "Costi personalizzati",
        "sidebar.notaio.label": "Oneri notaio per l'acquisto (€)",
        "sidebar.notaio.help": (
            "Onorario notarile + imposte di registro, ipotecaria e catastale"
        ),
        "sidebar.perizia.label": "Perizia immobile (€)",
        "sidebar.perizia.help": (
            "Perizia tecnica richiesta dalla banca prima dell'erogazione"
        ),
        "sidebar.ass_inc.label": "Assicurazione incendio (€)",
        "sidebar.ass_inc.help": (
            "Polizza incendio/scoppio: obbligatoria per il perfezionamento dell'ipoteca"
        ),
        "sidebar.ass_vita.label": "Assicurazione vita (€)",
        "sidebar.ass_vita.help": (
            "Polizza vita decrescente: protegge il mutuo in caso di decesso del mutuatario"
        ),
        "sidebar.donaz.label": "Costo atti donazione (€)",
        "sidebar.donaz.help": (
            "Atto notarile di donazione della prima casa precedente (onorario + imposte)"
        ),
        "sidebar.kiron.label": "% mediatore creditizio",
        "sidebar.kiron.help": (
            "Commissione broker/mediatore creditizio sul capitale erogato"
        ),
        "sidebar.med_pct.label": "% agenzia immobiliare",
        "sidebar.med_pct.help": (
            "Provvigione agenzia immobiliare sul prezzo di acquisto"
            " (IVA 22% inclusa, max \u20ac5\u202f000)"
        ),

        # ── Tabs — labels ──────────────────────────────────────────────────────
        "tabs.risultati": "\U0001f4ca Overview sul Mutuo",
        "tabs.rent": "\U0001f4c8 Valutazione Investimento",
        "tabs.inverse": "\U0001f4a1 Cosa Posso Permettermi?",
        "tabs.amort": "\U0001f4c5 Piano di Ammortamento",
        "tabs.sensitivity": "\U0001f50d Analisi di Sensibilit\u00e0",
        "tabs.estinzione": "\U0001f4d0 Estinzione Anticipata",
        "tabs.metodologia": "\U0001f4d6 Metodologia",

        # ── Tabs — static section headers & labels ─────────────────────────────
        "tabs.inverse.budget_header": "Budget di riferimento personalizzabile",
        "tabs.inverse.budget_cash.label": "Budget cash disponibile (\u20ac)",
        "tabs.inverse.pct_ref.label": "% Anticipo di riferimento",
        "tabs.estinzione.header": "Parametri estinzione anticipata",
        "tabs.estinzione.anno.label": "Anno di estinzione",
        "tabs.estinzione.anno.help": "Anno in cui estingui il mutuo residuo",
        "tabs.estinzione.r_alt.label": "Rendimento investimento alternativo",
        "tabs.estinzione.r_alt.help": (
            "Tasso che otterresti investendo il saldo residuo altrove"
        ),
        "tabs.estinzione.detr.label": "Detrazione interessi",
        "tabs.estinzione.detr.switch": "Applica 19% detraibilit\u00e0 (prima casa)",
        "tabs.estinzione.detr.help": (
            "Riduce il tasso effettivo del mutuo (max \u20ac4\u202f000/anno)"
        ),

        # ── Results tab ────────────────────────────────────────────────────────
        "risultati.kpi.rata": "Rata mensile",
        "risultati.kpi.totale_interessi": "Totale interessi",
        "risultati.kpi.totale_pagato": "Totale pagato",
        "risultati.kpi.costo_totale": "Costo totale acquisto",
        "risultati.kpi.ltv": "LTV",
        "risultati.kpi.tan": "TAN effettivo",
        "risultati.kpi.taeg": "TAEG stimato",
        "risultati.section.costi": "Riepilogo costi iniziali",
        "risultati.section.piano": "Piano rata nel tempo",
        "risultati.chart.costi_title": "Composizione costi di acquisto",
        "risultati.chart.piano_title": "Evoluzione del debito residuo",

        # ── Amortization tab ───────────────────────────────────────────────────
        "amort.section.header": "Piano di ammortamento completo",
        "amort.col.anno": "Anno",
        "amort.col.mese": "Mese",
        "amort.col.rata": "Rata",
        "amort.col.quota_cap": "Quota capitale",
        "amort.col.quota_int": "Quota interessi",
        "amort.col.debito_res": "Debito residuo",

        # ── Sensitivity tab ────────────────────────────────────────────────────
        "sensitivity.section.header": "Analisi di sensibilit\u00e0",
        "sensitivity.axis.tasso": "Tasso (%)",
        "sensitivity.axis.durata": "Durata (anni)",
        "sensitivity.axis.rata": "Rata mensile (\u20ac)",
        "sensitivity.axis.interessi": "Totale interessi (\u20ac)",

        # ── Estinzione tab ─────────────────────────────────────────────────────
        "estinzione.section.header": "Analisi estinzione anticipata",
        "estinzione.kpi.risparmio": "Risparmio interessi",
        "estinzione.kpi.costo_opp": "Costo opportunit\u00e0",
        "estinzione.kpi.convenienza": "Convenienza netta",
        "estinzione.chart.title": "Confronto scenari",

        # ── Inverse tab ────────────────────────────────────────────────────────
        "inverse.section.header": "Cosa puoi permetterti",
        "inverse.col.prezzo": "Prezzo max",
        "inverse.col.mutuo": "Mutuo",
        "inverse.col.anticipo": "Anticipo",
        "inverse.col.rata": "Rata/mese",
        "inverse.col.ltv": "LTV",

        # ── Investment (rent) tab ──────────────────────────────────────────────
        "rent.section.header": "Valutazione investimento immobiliare",
        "rent.input.affitto.label": "Canone mensile (€)",
        "rent.input.affitto.help": "Canone lordo mensile atteso",
        "rent.input.regime.label": "Regime fiscale",
        "rent.input.regime.ordinario": "IRPEF ordinaria",
        "rent.input.regime.cedolare_21": "Cedolare Secca 21%",
        "rent.input.regime.cedolare_10": "Cedolare Secca 10% (conc.)",
        "rent.input.imu.label": "IMU (%)",
        "rent.input.imu.help": "Aliquota IMU comunale",
        "rent.input.costi_vendita.label": "Costi vendita (%)",
        "rent.input.costi_vendita.help": "Agenzia + tasse sulla vendita",
        "rent.input.anno_uscita.label": "Anno uscita",
        "rent.input.anno_uscita.help": "Anno in cui vendi l'immobile",
        "rent.input.mant_freq.label": "Manut. freq. (anni)",
        "rent.input.mant_costo.label": "Costo manut. (€)",
        "rent.input.ricerca_freq.label": "Ricerca inquilino (anni)",
        "rent.input.ricerca_costo.label": "Costo ricerca (€)",
        "rent.input.canone_step.label": "Rivalutazione canone (anni)",
        "rent.input.canone_pct.label": "% Rivalutazione",
        "rent.kpi.irr": "IRR",
        "rent.kpi.npv": "NPV",
        "rent.kpi.gross_yield": "Rendimento lordo",
        "rent.kpi.net_yield": "Rendimento netto",
        "rent.kpi.payback": "Payback",
        "rent.kpi.anni": "anni",
        "rent.chart.waterfall_title": "Flussi di cassa cumulati",
        "rent.chart.cashflow_title": "Flussi di cassa annuali",
    },

    # ── English ───────────────────────────────────────────────────────────────
    "en": {
        # ── App-level ──────────────────────────────────────────────────────────
        "app.title": "Mortgage Purchase Simulator for Rental Income",
        "app.subtitle": (
            "Analysis for purchasing a property in Italy via mortgage"
            " for rental income purposes."
        ),
        "app.footer": "Mortgage Rental Calculator \u00b7 All rights reserved",
        "app.theme_toggle": "Toggle dark mode",
        "app.lang_toggle": "Change language",
        "app.visits": "{n} visits",

        # ── Sidebar ────────────────────────────────────────────────────────────
        "sidebar.header": "Parameters",
        "sidebar.offerta.label": "Property price (\u20ac)",
        "sidebar.offerta.help": "Agreed price with the seller. Use the slider or type the value.",
        "sidebar.anticipo.label": "Down payment (\u20ac)",
        "sidebar.durata.label": "Duration (years)",
        "sidebar.tasso.label": "Annual rate",
        "sidebar.tipo.label": "Purchase type",
        "sidebar.tipo.prima": "Primary residence",
        "sidebar.tipo.prima_donaz": "Primary (if donating current one)",
        "sidebar.tipo.seconda": "Second home / Non-primary",
        "sidebar.tipo.help": (
            "Determines registration tax rate (2% / 9%) and IMU exemption eligibility."
        ),
        "sidebar.rendita.label": "Cadastral income (\u20ac)",
        "sidebar.rendita.help": "From the property's cadastral survey",
        "sidebar.mediatore.label": "Include agency commission",
        "sidebar.adv_toggle": "Custom costs",
        "sidebar.notaio.label": "Notary fees for purchase (\u20ac)",
        "sidebar.notaio.help": "Notary fee + registration, mortgage and cadastral taxes",
        "sidebar.perizia.label": "Property appraisal (\u20ac)",
        "sidebar.perizia.help": "Technical appraisal required by the bank before disbursement",
        "sidebar.ass_inc.label": "Fire insurance (\u20ac)",
        "sidebar.ass_inc.help": "Fire/explosion policy: mandatory for mortgage completion",
        "sidebar.ass_vita.label": "Life insurance (\u20ac)",
        "sidebar.ass_vita.help": (
            "Decreasing term life policy: protects the mortgage in case of death"
        ),
        "sidebar.donaz.label": "Donation deed costs (\u20ac)",
        "sidebar.donaz.help": (
            "Notarial deed for donating previous primary residence (fee + taxes)"
        ),
        "sidebar.kiron.label": "% mortgage broker",
        "sidebar.kiron.help": "Broker/mortgage advisor commission on loan amount",
        "sidebar.med_pct.label": "% real estate agency",
        "sidebar.med_pct.help": (
            "Real estate agency commission on purchase price"
            " (VAT 22% included, max \u20ac5,000)"
        ),

        # ── Tabs — labels ──────────────────────────────────────────────────────
        "tabs.risultati": "\U0001f4ca Mortgage Overview",
        "tabs.rent": "\U0001f4c8 Investment Analysis",
        "tabs.inverse": "\U0001f4a1 What Can I Afford?",
        "tabs.amort": "\U0001f4c5 Amortization Schedule",
        "tabs.sensitivity": "\U0001f50d Sensitivity Analysis",
        "tabs.estinzione": "\U0001f4d0 Early Repayment",
        "tabs.metodologia": "\U0001f4d6 Methodology",

        # ── Tabs — static section headers & labels ─────────────────────────────
        "tabs.inverse.budget_header": "Customizable Reference Budget",
        "tabs.inverse.budget_cash.label": "Available cash budget (\u20ac)",
        "tabs.inverse.pct_ref.label": "% Reference down payment",
        "tabs.estinzione.header": "Early repayment parameters",
        "tabs.estinzione.anno.label": "Repayment year",
        "tabs.estinzione.anno.help": "Year in which you repay the remaining mortgage",
        "tabs.estinzione.r_alt.label": "Alternative investment return",
        "tabs.estinzione.r_alt.help": (
            "Rate you would earn by investing the remaining balance elsewhere"
        ),
        "tabs.estinzione.detr.label": "Interest deductibility",
        "tabs.estinzione.detr.switch": "Apply 19% deductibility (primary home)",
        "tabs.estinzione.detr.help": (
            "Reduces effective mortgage rate (max \u20ac4,000/year)"
        ),

        # ── Results tab ────────────────────────────────────────────────────────
        "risultati.kpi.rata": "Monthly payment",
        "risultati.kpi.totale_interessi": "Total interest",
        "risultati.kpi.totale_pagato": "Total paid",
        "risultati.kpi.costo_totale": "Total purchase cost",
        "risultati.kpi.ltv": "LTV",
        "risultati.kpi.tan": "Effective TAN",
        "risultati.kpi.taeg": "Estimated APRC",
        "risultati.section.costi": "Initial cost summary",
        "risultati.section.piano": "Payment schedule over time",
        "risultati.chart.costi_title": "Purchase cost breakdown",
        "risultati.chart.piano_title": "Outstanding balance evolution",

        # ── Amortization tab ───────────────────────────────────────────────────
        "amort.section.header": "Full amortization schedule",
        "amort.col.anno": "Year",
        "amort.col.mese": "Month",
        "amort.col.rata": "Payment",
        "amort.col.quota_cap": "Principal",
        "amort.col.quota_int": "Interest",
        "amort.col.debito_res": "Outstanding balance",

        # ── Sensitivity tab ────────────────────────────────────────────────────
        "sensitivity.section.header": "Sensitivity analysis",
        "sensitivity.axis.tasso": "Rate (%)",
        "sensitivity.axis.durata": "Duration (years)",
        "sensitivity.axis.rata": "Monthly payment (\u20ac)",
        "sensitivity.axis.interessi": "Total interest (\u20ac)",

        # ── Estinzione tab ─────────────────────────────────────────────────────
        "estinzione.section.header": "Early repayment analysis",
        "estinzione.kpi.risparmio": "Interest savings",
        "estinzione.kpi.costo_opp": "Opportunity cost",
        "estinzione.kpi.convenienza": "Net benefit",
        "estinzione.chart.title": "Scenario comparison",

        # ── Inverse tab ────────────────────────────────────────────────────────
        "inverse.section.header": "What you can afford",
        "inverse.col.prezzo": "Max price",
        "inverse.col.mutuo": "Mortgage",
        "inverse.col.anticipo": "Down payment",
        "inverse.col.rata": "Monthly payment",
        "inverse.col.ltv": "LTV",

        # ── Investment (rent) tab ──────────────────────────────────────────────
        "rent.section.header": "Real estate investment analysis",
        "rent.input.affitto.label": "Monthly rent (\u20ac)",
        "rent.input.affitto.help": "Expected gross monthly rent",
        "rent.input.regime.label": "Tax regime",
        "rent.input.regime.ordinario": "Standard IRPEF",
        "rent.input.regime.cedolare_21": "Flat tax 21%",
        "rent.input.regime.cedolare_10": "Flat tax 10% (conc.)",
        "rent.input.imu.label": "IMU (%)",
        "rent.input.imu.help": "Municipal IMU rate",
        "rent.input.costi_vendita.label": "Selling costs (%)",
        "rent.input.costi_vendita.help": "Agency + taxes on sale",
        "rent.input.anno_uscita.label": "Exit year",
        "rent.input.anno_uscita.help": "Year in which you sell the property",
        "rent.input.mant_freq.label": "Maint. freq. (years)",
        "rent.input.mant_costo.label": "Maint. cost (\u20ac)",
        "rent.input.ricerca_freq.label": "Tenant search (years)",
        "rent.input.ricerca_costo.label": "Search cost (\u20ac)",
        "rent.input.canone_step.label": "Rent review (years)",
        "rent.input.canone_pct.label": "% Review rate",
        "rent.kpi.irr": "IRR",
        "rent.kpi.npv": "NPV",
        "rent.kpi.gross_yield": "Gross yield",
        "rent.kpi.net_yield": "Net yield",
        "rent.kpi.payback": "Payback",
        "rent.kpi.anni": "years",
        "rent.chart.waterfall_title": "Cumulative cash flows",
        "rent.chart.cashflow_title": "Annual cash flows",
    },
}


def t(key: str, lang: str | None = None) -> str:
    """Return the translated string for *key* in the given *lang*.

    Falls back to Italian if the key or language is not found.
    Unknown keys are returned as-is so they are always visible.
    """
    lang = lang or "it"
    bucket = _T.get(lang, _T["it"])
    return bucket.get(key, _T["it"].get(key, key))
