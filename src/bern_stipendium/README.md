# Bern Scholarship (Stipendium) — OpenFisca Implementation

Modelling of the Bernese **Gesetz über die Ausbildungsbeiträge (ABG,
BSG 438.31)** and the accompanying **Verordnung (ABV, BSG 438.312)** —
eligibility logic plus the two-budget Fehlbetragsrechnung that determines
the CHF amount of Stipendium and Darlehen.

## Legal sources

* ABG Art. 1–3, 6–11, 12–16 — https://www.belex.sites.be.ch/data/438.31/de
* ABV Art. 1–34 (incl. Anhang A11 cost tables) —
  https://www.belex.sites.be.ch/data/438.312/de

## Structure

```
bern_stipendium/
├── entities.py                       # Person + Household with roles
├── system.py                         # CountryTaxBenefitSystem entry point
├── variables/
│   ├── enums.py                      # Staatsangehoerigkeit, Wohnform, Zivilstand, …
│   ├── inputs.py                     # Decomposed inputs (StG-aligned)
│   ├── familienbudget.py             # Art. 13–24 ABV (parents' budget)
│   ├── persoenliches_budget.py       # Art. 25–33 ABV (trainee's budget)
│   └── eligibility.py                # Eligibility gates + Stipendium/Darlehen amounts
├── parameters/
│   ├── stipendium/                   # Age limits, max duration, tertiary quote
│   ├── familienbudget/               # Anhang A11 family-budget tables
│   ├── persoenliches_budget/         # Anhang A11 personal-budget tables
│   ├── vermoegen/                    # 15 % Anrechnungsquote, Selbst.-Freibetrag
│   ├── eigener_haushalt/             # Mindestalter 20, Pendelzeit 90 Min.
│   ├── partnerschaft/                # Faktische Partnerschaft Mindestjahre
│   └── darlehen/                     # 50'000 CHF lebenslange Höchstgrenze
└── tests/
    ├── stipendium_anspruch.yaml      # Eligibility-gate scenarios
    ├── familienbudget.yaml           # Familienbudget Saldo + Verteilung
    ├── persoenliches_budget.yaml     # Persönliches Budget + Pro-Kopf-Anteil
    └── darlehen.yaml                 # Darlehen-Berechnung und 50k-Cap
```

## Entity model

The `Household` group entity uses **unique roles** so that Art. 14 ABV (joint
vs. separate parental budgets) and Art. 32 ABV (married/partnered trainees)
work correctly:

| Role               | Max | Purpose                                                                       |
|--------------------|-----|-------------------------------------------------------------------------------|
| `auszubildender`   | 1   | Applicant for the Stipendium / Darlehen                                       |
| `parent_a`         | 1   | First legal parent (Familienbudget unless `parent_a_zahlt_unterhalt`)         |
| `parent_b`         | 1   | Second legal parent (same treatment)                                          |
| `partner`          | 1   | Spouse / eingetragener Partner / qualifying faktischer Lebenspartner          |
| `kind_im_haushalt` | —   | Children in the parental household (drive Haushaltsgrösse, Pro-Kopf-Anteil)   |

## Calculation pipeline

```
inputs.py (per-Person tax-veranlagung values, Wohnform, …)
    │
    ▼
familienbudget.py  ── Art. 13–24 ABV ───────────────────────────┐
  ├─ familienbudget_einkommen     (Art. 15)                     │
  ├─ familienbudget_vermoegensanrechnung  (Art. 16: 15 %)       │
  ├─ familienbudget_lebenshaltungskosten  (Art. 17–22)          │
  ├─ familienbudget_freibetraege_total    (Art. 21)             │
  ├─ familienbudget_saldo                                       │
  ├─ familienbudget_ueberschuss_anteil_persoenlich (Art. 23) ──┐│
  └─ familienbudget_fehlbetrag_pro_kopf_anteil      (Art. 24) ─┐│
                                                              ││
                                                              ▼▼
persoenliches_budget.py  ── Art. 25–33 ABV
  ├─ persoenlich_einkommen            (+Art. 23 surplus share)
  ├─ persoenlich_vermoegensanrechnung
  ├─ persoenlich_ausbildungskosten / grundbedarf / wohnkosten / kk
  ├─ persoenlich_situationsbedingte_kosten (incl. Art. 33 Abs. 1 commute)
  ├─ anerkannte_ausbildungskosten      (+Art. 24 share if parental home)
  └─ anrechenbare_mittel_total
    │
    ▼
eligibility.py  ── Art. 10–16 ABG
  ├─ fehlbetrag = max(kosten − mittel, 0)  ÷ persoenlich_personen_anzahl  (Art. 32)
  ├─ stipendium_anspruch  =  alle Eligibilitäts-Gates
  ├─ stipendium_betrag    =  fehlbetrag × stipendium_quote
  └─ darlehen_betrag      =  Art. 10 Abs. 1 / 2 + 50k-Cap (Art. 11 Abs. 1)
```

## Mapping legal text → code

### ABG (Gesetz)

| Legal section                                                   | OpenFisca artefact                                      |
|-----------------------------------------------------------------|---------------------------------------------------------|
| Art. 10 Abs. 1 ABG — Zweitausbildung nur Darlehen               | `stipendium_grundsaetzlich_ausgeschlossen`, `darlehen_betrag` |
| Art. 10 Abs. 2 ABG — Tertiär ab Jahr 4: 2/3 Stipendium + 1/3 Darlehen | `stipendium_quote`, `darlehen_betrag`            |
| Art. 11 Abs. 1 ABG — Höchstbetrag Darlehen 50'000 CHF           | `darlehen.maximalbetrag` (Parameter)                    |
| Art. 12 Abs. 1, Art. 13 ABG — Stipendienrechtlicher Wohnsitz    | `hat_stipendienrechtlichen_wohnsitz_bern`               |
| Art. 12 Abs. 1 lit. b–d ABG — Persönlicher Status               | `erfuellt_persoenlichen_status`                         |
| Art. 14 Abs. 1 ABG — Max. 12 Beitragsjahre                      | `maximale_beitragsdauer_eingehalten`                    |
| Art. 14 Abs. 4 ABG — Altersgrenze 35 J. + Ausnahmen             | `altersgrenze_eingehalten`                              |
| Art. 15 Abs. 1 ABG — Bedürftigkeitsgrundsatz                    | `beduerftig`                                            |
| Art. 15 Abs. 2 ABG — Verzicht ab 25 J. / 4 J. Erwerbstätigkeit  | `verzicht_auf_anrechnung_eltern`                        |
| Art. 16 ABG — Fehlbetragsrechnung                               | `fehlbetrag`                                            |
| **Gesamtanspruch**                                              | **`stipendium_anspruch` → `stipendium_betrag`, `darlehen_betrag`** |

### ABV (Verordnung)

| Legal section                                       | OpenFisca artefact                              |
|-----------------------------------------------------|-------------------------------------------------|
| Art. 13 ABV — Fehlbetragsrechnung Grundsatz         | Pipeline split: `familienbudget` + `persoenliches_budget` |
| Art. 14 ABV — Familienbudget Konstellation          | `parent_a_zaehlt_im_familienbudget`, `…_b`      |
| Art. 14 Abs. 4 ABV — Unterhaltspflichtiger Elternteil | Inputs `parent_X_zahlt_unterhalt`             |
| Art. 15 ABV — Einkommen im Familienbudget           | `familienbudget_einkommen`                      |
| Art. 16 ABV — Vermögensanrechnung 15 %              | `familienbudget_vermoegensanrechnung`           |
| Art. 18 / Anhang A11.1 — Grundbedarf                | `familienbudget_grundbedarf`, Parameter-Tabelle |
| Art. 19 / Anhang A11.2 — Wohnkosten Familienbudget  | `familienbudget_wohnkosten`                     |
| Art. 20 / Anhang A11.7 — Krankenkasse               | `familienbudget_krankenkasse`                   |
| Art. 21 / Anhang A11.3 + A11.8 — Integrationszulage + Einkommensfreibetrag (Cap 13'200) | `familienbudget_freibetraege_total` |
| Art. 22 ABV — Situationsbedingte Kosten (Steuern, Berufskosten) | `familienbudget_situationsbedingte_kosten` |
| Art. 23 Abs. 1 / 3 ABV — Saldoteilung bei Überschuss | `familienbudget_ueberschuss_anteil_persoenlich` |
| Art. 24 ABV — Pro-Kopf-Anteil bei Fehlbetrag        | `familienbudget_fehlbetrag_pro_kopf_anteil`     |
| Art. 26 ABV — Einkommen im persönlichen Budget      | `persoenlich_einkommen`                         |
| Art. 26 Abs. 3 / Anhang A11.10 — Erwerbseinkommen-Freibetrag Tertiär 6'000 | Parameter + `persoenlich_einkommen` |
| Art. 27 ABV — Vermögensanrechnung 15 %              | `persoenlich_vermoegensanrechnung`              |
| Art. 28 / Anhang A11.4 — Ausbildungskosten Höchstansatz | `persoenlich_ausbildungskosten`             |
| Art. 30 ABV — Eigener Haushalt (Mindestalter 20, Pendelzeit > 90 Min., …) | `eigener_haushalt_anerkannt`  |
| Art. 31 / Anhang A11.6 — Wohnkosten eigener Haushalt | `persoenlich_wohnkosten`                       |
| Art. 32 Abs. 1 ABV — Pro-Kopf-Anteil persönliches Budget bei Verheirateten | `persoenlich_personen_anzahl`, `fehlbetrag` |
| Art. 32 Abs. 2 ABV — Faktische Partnerschaft (≥ 5 J. ODER Kind) | `faktische_partnerschaft_qualifiziert` |
| Art. 33 ABV — Situationsbedingte Kosten persönliches Budget (Fahrkosten, Verpflegung, Kinderbetreuung) | `persoenlich_situationsbedingte_kosten` |

## Running the tests

```bash
openfisca test src/bern_stipendium/tests/ --country-package bern_stipendium
```

## Example simulation

```python
from openfisca_core.simulation_builder import SimulationBuilder
from bern_stipendium.system import CountryTaxBenefitSystem

tbs = CountryTaxBenefitSystem()
situation = {
    "persons": {
        "anna": {
            "wohnsitz_grundlage": {"2024": "finanziell_unabhaengig"},
            "staatsangehoerigkeit": {"2024": "schweizer"},
            "ausbildungstyp": {"2024": "erstausbildung"},
            "ausbildungsstufe": {"2024": "tertiaerstufe"},
            "ausbildungsstaette_anerkannt": {"2024": True},
            "in_ausbildung": {"2024": True},
            "wohnform": {"2024": "eigener_haushalt"},
            "alter": {"2024": 22},
            "aktuelles_ausbildungsjahr": {"2024": 1},
            "total_einkuenfte_steuerveranlagung": {"2024": 0},
            "tatsaechliche_ausbildungskosten": {"2024": 3000},
        },
    },
    "households": {
        "h1": {
            "auszubildende": ["anna"],
            "wohnkosten_persoenlich_tatsaechlich": {"2024": 11000},
        },
    },
}
sim = SimulationBuilder().build_from_dict(tbs, situation)
print("Stipendium:", sim.calculate("stipendium_betrag", "2024"))
print("Darlehen:", sim.calculate("darlehen_betrag", "2024"))
```

## Known limitations (deliberately not modelled)

* **Hardship cases (Art. 34 ABV)** — discretionary; out of scope.
* **Loan repayment / interest schedule (Art. 11 Abs. 2 ABG)** — model
  computes only the entitlement amount, not amortisation.
* **Provisional-vs-final tax assessment workflow (Art. 15 Abs. 3–5 ABV)** —
  administrative; the model assumes a single given assessment value per
  simulation period.
* **Art. 14 Abs. 3 ABV (separate parental Familienbudgets)** — modelled as a
  single aggregate Familienbudget that sums per-parent contributions
  weighted by the `parent_X_zaehlt_im_familienbudget` flags. Strictly per
  ABV one would compute two separate budgets and aggregate their flows;
  for typical separated-parent cases the aggregate is correct when only
  one parent contributes (Unterhalt or absent parent) and conservative
  otherwise.
* **Art. 9 ABG (Einschränkung bei ungenügenden Mitteln)** — budget-procedural
  lever; not modelled.
* **Art. 14 Abs. 5 ABG (no retroactive grants)** — procedural intake rule.
