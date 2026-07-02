"""Static methodology tab — explains every formula and input used in the app."""
from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html

# ── Reusable formula block style ─────────────────────────────────────────────
_FORMULA = {
    "background": "#f1f5f9",
    "border": "1px solid #e2e8f0",
    "borderLeft": "4px solid #3b82f6",
    "borderRadius": "6px",
    "padding": "10px 14px",
    "fontFamily": "monospace",
    "fontSize": "0.9rem",
    "margin": "10px 0",
    "overflowX": "auto",
    "whiteSpace": "pre",
}

_NOTE = {
    "background": "#fffbeb",
    "border": "1px solid #fde68a",
    "borderRadius": "6px",
    "padding": "8px 12px",
    "fontSize": "0.82rem",
    "color": "#78350f",
    "margin": "8px 0",
}

_BADGE = {
    "display": "inline-block",
    "background": "#e0f2fe",
    "color": "#075985",
    "borderRadius": "4px",
    "padding": "1px 7px",
    "fontSize": "0.78rem",
    "fontWeight": "600",
    "marginRight": "4px",
}


def _var(text: str) -> html.Span:
    return html.Span(text, style={"fontStyle": "italic", "fontFamily": "monospace",
                                  "color": "#1e40af"})


def _code(text: str) -> html.Code:
    return html.Code(text, style={"background": "#f1f5f9", "padding": "1px 5px",
                                   "borderRadius": "3px", "fontSize": "0.88rem"})


def _section(title: str, *children) -> dbc.AccordionItem:
    return dbc.AccordionItem(children, title=title)


# ═══════════════════════════════════════════════════════════════════════════════
#  Section builders
# ═══════════════════════════════════════════════════════════════════════════════

def _sec_pmt() -> dbc.AccordionItem:
    return _section("1 · Rata mensile — Piano di ammortamento (PMT)",
        html.P([
            "Il mutuo segue il ", html.Strong("piano di ammortamento alla francese"),
            " (rate mensili costanti). La rata è calcolata dalla formula PMT:",
        ]),
        html.Div("Rata = M × r_m / (1 − (1 + r_m)^(−n))", style=_FORMULA),
        html.Ul([
            html.Li([_var("M"), " = capitale erogato = Prezzo − Anticipo"]),
            html.Li([_var("r_m"), " = tasso mensile = Tasso annuo / 12"]),
            html.Li([_var("n"), " = numero rate = Durata (anni) × 12"]),
        ], className="small mb-2"),
        html.P([
            "Ogni rata è composta da ", html.Strong("interessi"), " (saldo residuo × r_m) e ",
            html.Strong("quota capitale"), " (Rata − interessi). "
            "Con l'avanzare del piano la quota capitale cresce e gli interessi scendono, "
            "ma la rata totale rimane costante.",
        ], className="small"),
        html.Div([
            html.Strong("Saldo residuo al mese t:"), html.Br(),
            html.Code("S_t = M × [(1+r_m)^n − (1+r_m)^t] / [(1+r_m)^n − 1]",
                      style={"fontFamily": "monospace"}),
        ], style=_FORMULA),
        html.Div([
            html.Span("Input utilizzati: ", className="fw-semibold"),
            _code("Prezzo immobile"), ", ", _code("Anticipo"), ", ",
            _code("Durata (anni)"), ", ", _code("Tasso annuo"),
        ], className="small mt-2"),
    )


def _sec_costi() -> dbc.AccordionItem:
    return _section("2 · Costi di acquisto — Imposte e spese accessorie",
        html.P([
            "Il ", html.Strong("Costo Iniziale Totale"), " C₀ include anticipo + "
            "tutte le spese accessorie. È il denominatore del Cash-on-Cash return "
            "e il capitale di partenza nel calcolo di IRR e NPV.",
        ], className="small"),
        html.H6("Imposta di registro", className="mt-2"),
        html.P("La base imponibile è il valore catastale rivalutato (non il prezzo di mercato):",
               className="small"),
        html.Div(
            "Valore_catastale = Rendita × 1.05 × coefficiente\n\n"
            "  Prima casa  → coeff. 110  →  Imposta registro = Valore_cat × 2%\n"
            "  Seconda casa → coeff. 126  →  Imposta registro = Valore_cat × 9%\n\n"
            "  (minimo €1 000 per entrambe le aliquote)",
            style=_FORMULA,
        ),
        html.Div([
            "La rivalutazione ISTAT del 5% (fattore 1.05) è obbligatoria per legge "
            "(D.M. 14/12/1991). Il coefficiente catastale 110/126 è quello previsto "
            "per le categorie abitative ordinarie A/2–A/7.",
        ], style=_NOTE),
        html.H6("Imposta sostitutiva ipotecaria", className="mt-2"),
        html.Div(
            "I_sost = Mutuo × 0.25%   (prima casa, D.P.R. 601/1973 art. 17)\n"
            "I_sost = Mutuo × 2.00%   (seconda casa / non agevolata)",
            style=_FORMULA,
        ),
        html.H6("Riepilogo voci di spesa", className="mt-2"),
        dbc.Table([
            html.Thead(html.Tr([
                html.Th("Voce"), html.Th("Formula / Calcolo"), html.Th("Note"),
            ])),
            html.Tbody([
                html.Tr([html.Td("Anticipo"), html.Td("inserito"),
                         html.Td("Liquidità versata al rogito")]),
                html.Tr([html.Td("Imposta di registro"), html.Td("Valore_cat × 2% / 9%"),
                         html.Td("Base: valore catastale, non prezzo")]),
                html.Tr([html.Td("Imposta sostitutiva ipotecaria"),
                         html.Td("Mutuo × 0.25% / 2%"),
                         html.Td("Sostituisce tutte le imposte ipotecarie")]),
                html.Tr([html.Td("Commissione bancaria"),
                         html.Td("Mutuo × 1%"),
                         html.Td("Spesa di istruttoria bancaria")]),
                html.Tr([html.Td("Mediatore creditizio"),
                         html.Td("Mutuo × % configurabile"),
                         html.Td("Solo se switch attivo")]),
                html.Tr([html.Td("Perizia immobile"), html.Td("€ inserito"),
                         html.Td("Obbligatoria per erogazione mutuo")]),
                html.Tr([html.Td("Assicurazione incendio/scoppio"),
                         html.Td("€ inserito"),
                         html.Td("Obbligatoria per legge (ipoteca)")]),
                html.Tr([html.Td("Assicurazione vita"),
                         html.Td("€ inserito"), html.Td("Richiesta dalla banca")]),
                html.Tr([html.Td("Oneri notarili"), html.Td("€ inserito"),
                         html.Td("Onorario + spese atti")]),
                html.Tr([html.Td("Provvigione agenzia (+IVA 22%)"),
                         html.Td("min(Prezzo × %, €5 000) × 1.22"),
                         html.Td("IVA inclusa nel costo")]),
                html.Tr([html.Td("Atti donazione (prima_donaz)"),
                         html.Td("€ inserito"),
                         html.Td("Solo per la voce 'dono la prima casa'")]),
            ]),
        ], size="sm", bordered=True, hover=True, responsive=True, className="small"),
        html.Div([
            html.Span("Input utilizzati: ", className="fw-semibold"),
            _code("Prezzo"), ", ", _code("Anticipo"), ", ", _code("Rendita catastale"), ", ",
            _code("Tipo acquisto"), ", tutti i campi nella sezione ",
            html.Em("Costi personalizzati"),
        ], className="small mt-2"),
    )


def _sec_imu() -> dbc.AccordionItem:
    return _section("3 · IMU annuale",
        html.P([
            "L'", html.Strong("Imposta Municipale Propria"),
            " (D.L. 201/2011, art. 13) è calcolata sulla rendita catastale rivalutata:",
        ], className="small"),
        html.Div(
            "IMU_annua = Rendita × 1.05 × 160 × (aliquota / 100)\n\n"
            "IMU_mensile = IMU_annua / 12",
            style=_FORMULA,
        ),
        html.Ul([
            html.Li([html.Strong("Rendita"), " = rendita catastale dalla visura"]),
            html.Li(["1.05 = rivalutazione ISTAT (identica all'imposta di registro)"]),
            html.Li(["160 = moltiplicatore catastale per A/2, A/3, A/4 ",
                     "(abitazioni civili ordinarie)"]),
            html.Li(["Aliquota standard: 0.86% (aliquota base 0.76% + 0.1% extra delibera "
                     "comunale; max 1.06%)"]),
        ], className="small"),
        html.Div([
            html.Strong("Esenzioni: "),
            "la prima casa non di lusso (categorie A/2–A/7, escluse A/1, A/8, A/9) "
            "è completamente esente da IMU. Quando si sceglie 'Prima casa' o "
            "'1a casa (se prima dono l'altra)' nel tipo acquisto, l'aliquota IMU "
            "viene automaticamente impostata a 0.",
        ], style=_NOTE),
        html.Div([
            html.Span("Input utilizzati: ", className="fw-semibold"),
            _code("Rendita catastale"), ", ", _code("Tipo acquisto"), ", ",
            _code("Aliquota IMU"), " (configurabile nel tab Investimento)",
        ], className="small mt-2"),
    )


def _sec_cashflow() -> dbc.AccordionItem:
    return _section("4 · Cashflow mensile operativo",
        html.P("Il cashflow mensile netto si costruisce per sottrazione:",
               className="small"),
        html.Div(
            "Affitto_eff   = Affitto_lordo × (1 − vacancy_rate)\n"
            "Tax_mensile   = Affitto_eff   × aliquota_fiscale\n"
            "Affitto_netto = Affitto_eff   − Tax_mensile\n\n"
            "Costi_op =   IMU_annua/12\n"
            "           + (Prezzo × mant_ord_%)/12\n"
            "           + (freq_mant_straord × costo_mant_straord)/12\n"
            "           + spese_fisse_annue/12\n"
            "           + (costo_ricerca_inq × freq_ricerca_inq)/12\n\n"
            "CF_netto_mese = Affitto_netto − Rata − Costi_op",
            style=_FORMULA,
        ),
        html.H6("Regime fiscale", className="mt-2"),
        dbc.Table([
            html.Thead(html.Tr([
                html.Th("Regime"), html.Th("Aliquota effettiva"), html.Th("Base imponibile"),
            ])),
            html.Tbody([
                html.Tr([html.Td("Cedolare Secca (21%)"), html.Td("21%"),
                         html.Td("100% del canone incassato")]),
                html.Tr([html.Td("Canone Concordato (10%)"), html.Td("10%"),
                         html.Td("100% del canone incassato")]),
                html.Tr([html.Td("IRPEF 35° scaglione"), html.Td("33.25%"),
                         html.Td("95% del canone (5% esente, art. 36 TUIR)")]),
                html.Tr([html.Td("IRPEF 43° scaglione"), html.Td("40.85%"),
                         html.Td("95% del canone (5% esente, art. 36 TUIR)")]),
            ]),
        ], size="sm", bordered=True, responsive=True, className="small"),
        html.P([
            html.Strong("Vacancy rate: "),
            "riduce l'affitto lordo dell'intera analisi. "
            "5% equivale a circa 18 giorni sfitti all'anno (tipico per abitazioni in buona posizione). "
            "10% equivale a circa 36 giorni. La perdita da vacancy non è fiscalmente deducibile.",
        ], className="small mt-2"),
        html.P([
            html.Strong("Ricerca inquilino: "),
            "costo/evento × frequenza (eventi/anno) diviso 12 = costo mensile medio. "
            "0.5 eventi/anno significa che mediamente si cambia inquilino ogni 2 anni. "
            "Questo costo è incluso nei costi operativi e contribuisce al waterfall e alla tabella dettaglio.",
        ], className="small"),
        html.Div([
            html.Span("Input utilizzati: ", className="fw-semibold"),
            "tutti i campi del pannello ", html.Em("Parametri investimento"),
        ], className="small mt-2"),
    )


def _sec_canone() -> dbc.AccordionItem:
    return _section("5 · Crescita del canone nel tempo",
        html.P([
            "La crescita del canone nel tempo si modella in due modalità:",
        ], className="small"),
        html.H6("Modalità bloccata (crescita = inflazione)"),
        html.Div(
            "Al mese m (m ≥ 1, anno y = floor((m−1)/12)):\n\n"
            "  rent_growth_m = (1 + r_inf_m)^(m−1)\n"
            "  r_inf_m = (1 + rivalutazione_annua)^(1/12) − 1\n\n"
            "Affitto_eff_m = Affitto_eff × rent_growth_m",
            style=_FORMULA,
        ),
        html.P("Il canone cresce mese per mese in modo continuo allo stesso tasso dell'inflazione generale.",
               className="small"),
        html.H6("Modalità disallacciata (crescita indipendente)"),
        html.Div(
            "  n_scatti = floor(y / S)   dove S = anni tra adeguamenti\n"
            "  rent_growth_m = (1 + g_canone)^(n_scatti × S)\n\n"
            "Esempio: g = 2%/anno, S = 4 anni (contratto concordato)\n"
            "  → al 4° anno: (1.02)^4 ≈ +8.24%\n"
            "  → all'8° anno: (1.02)^8 ≈ +17.2%\n"
            "  → tra 0°–4° anno: nessun aumento",
            style=_FORMULA,
        ),
        html.P([
            "Il canone si aggiorna in ", html.Strong("scatti discreti"),
            " ogni S anni — realisticamente fedele ai contratti italiani "
            "(libero = ogni 2 anni, concordato = ogni 4 anni secondo art. 2 L. 431/1998).",
        ], className="small"),
        html.Div([
            html.Strong("Nota: "),
            "i costi operativi crescono sempre con l'inflazione generale, "
            "indipendentemente dalla modalità scelta per il canone.",
        ], style=_NOTE),
        html.Div([
            html.Span("Input utilizzati: ", className="fw-semibold"),
            _code("Switch Disallaccia"), ", ", _code("Crescita %/anno"), ", ",
            _code("Adeguamento ogni N anni"), ", ", _code("Rivalutazione immobile %"),
        ], className="small mt-2"),
    )


def _sec_terminale() -> dbc.AccordionItem:
    return _section("6 · Valore terminale e P&L cumulato",
        html.P([
            "Al termine dell'orizzonte T (anno di uscita) si calcolano il ricavo di vendita "
            "e il guadagno o perdita complessiva.",
        ], className="small"),
        html.Div(
            "Valore_imm_T  = Prezzo × (1 + rivalutazione)^T\n\n"
            "Valore_terminale = Valore_imm_T × (1 − costi_vendita%) − S_(T×12)\n\n"
            "  dove S_(T×12) = saldo residuo del mutuo all'anno T",
            style=_FORMULA,
        ),
        html.Div([
            html.Strong("Anno di uscita T — tre casi:"), html.Br(),
            html.Ul([
                html.Li([html.Strong("T < durata: "),
                         "vendita anticipata con mutuo ancora in corso. "
                         "Il saldo residuo S_(T×12) è positivo e viene detratto dal ricavo. "
                         "Se il ricavo netto è negativo si genera un alert 'equity negativa'."]),
                html.Li([html.Strong("T = durata: "),
                         "vendita a fine mutuo. S = 0, ricavo = solo plusvalenza immobiliare."]),
                html.Li([html.Strong("T > durata: "),
                         "i mesi dopo la fine del mutuo contribuiscono con CF = affitto_netto − costi_op "
                         "(senza rata). Il calcolo IRR e NPV include questi extra anni post-mutuo."]),
            ], className="mb-0"),
        ], style=_NOTE),
        html.H6("P&L cumulato all'anno y", className="mt-2"),
        html.Div(
            "CF_op_cumulati_y = somma di tutti i CF mensili dall'anno 1 all'anno y\n\n"
            "Guadagno_equity_y = Valore_imm_y − S_(y×12) − C0\n\n"
            "P&L_totale_y = CF_op_cumulati_y + Guadagno_equity_y",
            style=_FORMULA,
        ),
        html.P([
            "Il P&L totale risponde alla domanda: ",
            html.Em("\"se vendessi oggi, quanto avrei guadagnato o perso rispetto al costo iniziale?\""),
        ], className="small"),
        html.Div([
            html.Span("Input utilizzati: ", className="fw-semibold"),
            _code("Rivalutazione immobile %"), ", ", _code("Costi vendita %"), ", ",
            _code("Anno di uscita T"),
        ], className="small mt-2"),
    )


def _sec_irr() -> dbc.AccordionItem:
    return _section("7 · IRR — Tasso Interno di Rendimento",
        html.P([
            "L'IRR è il tasso mensile r* che rende il NPV dell'investimento uguale a zero:",
        ], className="small"),
        html.Div(
            "NPV(r*) = 0\n\n"
            "dove:\n"
            "NPV(r) = −C0\n"
            "       + Σ(m=1 → T×12) [ CF_m / (1+r)^m ]\n"
            "       + Valore_terminale / (1+r)^(T×12)",
            style=_FORMULA,
        ),
        html.P([
            "Non esiste una soluzione analitica chiusa. L'equazione viene risolta numericamente "
            "con il ", html.Strong("metodo di Brent"),
            " (libreria scipy), ricercando la radice nell'intervallo "
            "[−9%/12, +50%/12]. L'IRR annualizzato è:",
        ], className="small"),
        html.Div("IRR_ann = (1 + r*)^12 − 1", style=_FORMULA),
        html.H6("Interpretazione", className="mt-2"),
        dbc.Table([
            html.Thead(html.Tr([html.Th("Condizione"), html.Th("Significato")])),
            html.Tbody([
                html.Tr([html.Td("IRR > tasso di sconto"),
                         html.Td("Investimento crea valore (NPV > 0) rispetto al benchmark")]),
                html.Tr([html.Td("IRR = tasso di sconto"),
                         html.Td("Investimento equivalente al benchmark (NPV = 0)")]),
                html.Tr([html.Td("IRR < tasso di sconto"),
                         html.Td("Meglio investire nel benchmark (NPV < 0)")]),
                html.Tr([html.Td("IRR non calcolabile"),
                         html.Td("CF tutti negativi o convergenza fallita (es. orizzonte troppo corto)")]),
            ]),
        ], size="sm", bordered=True, responsive=True, className="small"),
        html.P([
            html.Strong("Grafico IRR vs canone: "),
            "mostra l'IRR per valori di affitto lordo mensile compresi tra il 50% e il 200% "
            "del canone inserito, tenendo tutti gli altri parametri fissi. "
            "Utile per capire la ", html.Em("sensibilità"),
            " dell'investimento all'evoluzione del canone di mercato.",
        ], className="small mt-1"),
        html.Div([
            html.Span("Input utilizzati: ", className="fw-semibold"),
            "tutti i parametri del tab Investimento + ", _code("Anno di uscita T"),
        ], className="small mt-2"),
    )


def _sec_npv() -> dbc.AccordionItem:
    return _section("8 · NPV — Valore Attuale Netto",
        html.P([
            "Il NPV attualizza tutti i flussi futuri al ", html.Strong("tasso di sconto"),
            " (costo opportunità del capitale):",
        ], className="small"),
        html.Div(
            "NPV = −C0\n"
            "    + Σ(m=1 → T×12) [ CF_m / (1 + d_m)^m ]\n"
            "    + Valore_terminale / (1 + d_m)^(T×12)\n\n"
            "dove d_m = (1 + tasso_sconto_annuo)^(1/12) − 1",
            style=_FORMULA,
        ),
        html.P([
            "Il tasso di sconto rappresenta il ", html.Strong("rendimento che potresti ottenere"),
            " investendo lo stesso capitale altrove (BTP, mercato azionario, portafoglio bilanciato). "
            "Più è alto, più il futuro vale meno in termini attuali.",
        ], className="small"),
        dbc.Table([
            html.Thead(html.Tr([html.Th("Benchmark comune"), html.Th("Tasso di sconto consigliato")])),
            html.Tbody([
                html.Tr([html.Td("BTP decennale (risk-free italiano)"), html.Td("3.5%")]),
                html.Tr([html.Td("Portafoglio obbligazionario"), html.Td("3–4%")]),
                html.Tr([html.Td("Portafoglio bilanciato 60/40"), html.Td("5–6%")]),
                html.Tr([html.Td("Mercato azionario diversificato"), html.Td("7–8%")]),
            ]),
        ], size="sm", bordered=True, responsive=True, className="small"),
        html.P([
            html.Strong("Grafico NPV vs rivalutazione: "),
            "mostra come il NPV varia al variare della rivalutazione annua dell'immobile (da −2% a +7%). "
            "Evidenzia quanto il risultato finale sia sensibile all'apprezzamento del bene: "
            "in molti mercati italiani, la rivalutazione è il principale driver di redditività.",
        ], className="small mt-1"),
        html.Div([
            html.Span("Input utilizzati: ", className="fw-semibold"),
            _code("Tasso di sconto %"), ", ", _code("Anno di uscita T"),
            ", tutti i parametri cashflow",
        ], className="small mt-2"),
    )


def _sec_indicatori() -> dbc.AccordionItem:
    return _section("9 · Indicatori di redditività",
        html.P("Quattro indicatori misurano la redditività su assi diversi:",
               className="small"),
        dbc.Table([
            html.Thead(html.Tr([
                html.Th("Indicatore"), html.Th("Formula"), html.Th("Cosa misura"),
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(html.Strong("Gross Rental Yield")),
                    html.Td(html.Code("Affitto_lordo × 12 / Prezzo")),
                    html.Td("Rendimento lordo nominale del canone, senza costi né tasse"),
                ]),
                html.Tr([
                    html.Td(html.Strong("Cap Rate")),
                    html.Td(html.Code("NOI_pretax / Prezzo")),
                    html.Td("Reddito operativo netto ante-imposte canone sul valore dell'immobile"),
                ]),
                html.Tr([
                    html.Td(html.Strong("Net Yield")),
                    html.Td(html.Code("NOI_posttax / Prezzo")),
                    html.Td("Reddito operativo netto post-imposte canone sul valore dell'immobile"),
                ]),
                html.Tr([
                    html.Td(html.Strong("Cash-on-Cash")),
                    html.Td(html.Code("CF_netto_annuo / C0")),
                    html.Td("Rendimento effettivo sul capitale totale investito (anno 1)"),
                ]),
            ]),
        ], size="sm", bordered=True, responsive=True, className="small"),
        html.Div(
            "NOI_pretax  = Affitto_eff_annuo − Costi_op_annui    (ante imposte canone)\n"
            "NOI_posttax = Affitto_netto_annuo − Costi_op_annui  (post imposte canone)\n"
            "C0          = Costo iniziale totale (anticipo + tutte le spese di acquisto)",
            style=_FORMULA,
        ),
        html.H6("Canone di break-even", className="mt-2"),
        html.Div(
            "Affitto_BE = (Rata + Costi_op_base) / [(1 − vacancy%) × (1 − aliquota)]",
            style=_FORMULA,
        ),
        html.P([
            "È il canone lordo mensile minimo per avere un cashflow mensile netto ≥ 0. "
            "Se l'affitto di mercato è inferiore a questo valore, ogni mese si ha una perdita di liquidità "
            "(il mutuo non si ripaga da solo).",
        ], className="small"),
        html.Div([
            html.Strong("Differenza Cap Rate vs Gross Yield: "),
            "il Cap Rate deduce anche i costi operativi (IMU, manutenzione, spese fisse, ecc.) "
            "e la perdita da vacancy. È un indicatore più completo del semplice yield lordo.",
        ], style=_NOTE),
        html.Div([
            html.Span("Input utilizzati: ", className="fw-semibold"),
            "tutti i parametri del tab Investimento",
        ], className="small mt-2"),
    )


def _sec_estinzione() -> dbc.AccordionItem:
    return _section("10 · Estinzione anticipata — logica del confronto",
        html.P([
            "Il tab ", html.Strong("Estinzione Anticipata"), " risponde alla domanda: ",
            html.Em("\"conviene versare il saldo residuo del mutuo all'anno X, oppure investire quella liquidità?\""),
        ], className="small"),
        html.H6("NPV dell'estinzione"),
        html.P([
            "All'anno X hai in mano una cifra pari al saldo residuo S_X. "
            "Se estingui, risparmi le rate rimanenti; se investi, quella cifra cresce al tasso alternativo r_alt:",
        ], className="small"),
        html.Div(
            "NPV(Estingui) = −S_X + Rata × [1 − (1 + r_alt_m)^(−N_X)] / r_alt_m\n\n"
            "  S_X    = saldo residuo mutuo all'anno X  (formula sezione 1)\n"
            "  N_X    = (Durata − X) × 12  = rate rimanenti\n"
            "  r_alt_m = (1 + r_alt)^(1/12) − 1  = tasso mensile alternativo",
            style=_FORMULA,
        ),
        html.Ul([
            html.Li([html.Strong("NPV > 0"), ": estinguere è conveniente — "
                     "il risparmio sugli interessi futuri supera il mancato guadagno dal r_alt"]),
            html.Li([html.Strong("NPV < 0"), ": meglio investire — "
                     "il r_alt supera il costo effettivo del mutuo"]),
        ], className="small"),
        html.H6("Tasso di breakeven", className="mt-2"),
        html.P([
            "Il tasso r_alt* per cui NPV = 0 è il ", html.Strong("tasso di breakeven"),
            ". Coincide con il tasso effettivo del mutuo. Trovato numericamente con il metodo di Brent.",
        ], className="small"),
        html.H6("Tasso effettivo del mutuo (con detraibilità)", className="mt-2"),
        html.Div(
            "I_X    = S_(X−1)×12 × r_nom          (interessi pagati nell'anno X)\n"
            "Saving = min(I_X, €4 000) × 19%       (detrazione IRPEF art. 15 TUIR)\n\n"
            "r_eff  = r_nom − Saving / S_X",
            style=_FORMULA,
        ),
        html.Div([
            "La detraibilità del 19% sugli interessi passivi (max €4 000/anno) riduce "
            "il costo reale del mutuo per la prima casa. Questo innalza il tasso di breakeven: "
            "se il mutuo costa effettivamente meno del 3%, occorre trovare un investimento che batta anche questa soglia ridotta.",
        ], style=_NOTE),
        html.H6("Grafici del tab", className="mt-2"),
        html.Ul([
            html.Li([html.Strong("CF annuo da mutuo: "),
                     "confronta le rate pagate anno per anno con e senza l'estinzione anticipata"]),
            html.Li([html.Strong("Confronto cumulato da anno X: "),
                     "wealth_A (risparmio lineare) vs wealth_B (investimento composto). "
                     "Il punto di incrocio indica quando una strategia supera l'altra"]),
            html.Li([html.Strong("NPV vs tasso alternativo: "),
                     "mostra come il NPV dell'estinzione varia al variare del r_alt. "
                     "A sinistra del breakeven conviene estinguere; a destra conviene investire"]),
        ], className="small"),
        html.Div([
            html.Span("Input utilizzati: ", className="fw-semibold"),
            _code("Anno estinzione X"), ", ", _code("Rendimento alternativo %"), ", ",
            _code("Switch detraibilità 19%"), ", tutti i parametri sidebar (mutuo)",
        ], className="small mt-2"),
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  Public builder
# ═══════════════════════════════════════════════════════════════════════════════

def build_metodologia_tab() -> dbc.Tab:
    """Return the fully static '📚 Metodi e Formule' tab."""
    return dbc.Tab(
        label="📚 Metodi e Formule",
        tab_id="tab-metodologia",
        children=html.Div([
            html.Div([
                html.H4([html.I(className="bi bi-journal-text me-2"),
                         "Metodologia e Formule"],
                        className="fw-bold mb-1"),
                html.P(
                    "Riferimento tecnico completo per tutti i calcoli eseguiti dall'applicazione. "
                    "Apri le sezioni di interesse — ogni voce descrive la formula esatta, "
                    "le variabili di input coinvolte e come interpretare il risultato.",
                    className="text-muted small mb-3",
                ),
            ], className="mt-3"),
            dbc.Accordion(
                [
                    _sec_pmt(),
                    _sec_costi(),
                    _sec_imu(),
                    _sec_cashflow(),
                    _sec_canone(),
                    _sec_terminale(),
                    _sec_irr(),
                    _sec_npv(),
                    _sec_indicatori(),
                    _sec_estinzione(),
                ],
                always_open=True,
                start_collapsed=True,
                className="mb-4",
            ),
        ]),
    )
