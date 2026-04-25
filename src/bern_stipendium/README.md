# Bern Scholarship (Stipendium) — OpenFisca Implementation

Modelling of the Bernese **Gesetz über die Ausbildungsbeiträge (ABG)** and
the accompanying **Verordnung (ABV)**.

## Legal sources

* ABG Art. 1–3, 6–10, 12–16
* ABV (supplementary regulations)
* https://www.belex.sites.be.ch/data/438.31/de

## Structure

```
bern_stipendium/
├── entities.py                       # Person + Household + roles
├── system.py                         # CountryTaxBenefitSystem entry point
├── variables/
│   ├── enums.py                      # Staatsangehoerigkeit, Ausbildungstyp, …
│   ├── inputs.py                     # Variables supplied by the simulation
│   └── eligibility.py                # Computed legal conditions + amount
├── parameters/
│   └── stipendium/
│       ├── max_beitragsdauer_jahre.yaml          (Art. 14 Abs. 1 ABG: 12)
│       ├── altersgrenze_anspruch.yaml            (Art. 14 ABG: 35)
│       ├── altersgrenze_verzicht_eltern.yaml     (Art. 15 Abs. 2 ABG: 25)
│       ├── erwerbsjahre_verzicht_eltern.yaml     (Art. 15 Abs. 2 ABG: 4)
│       ├── eltern_quote_bei_verzicht.yaml        (Art. 15 Abs. 2 ABG / ABV)
│       ├── tertiaer_volle_quote_jahre.yaml       (Art. 10 ABG: 3)
│       └── tertiaer_reduzierte_quote.yaml        (Art. 10 ABG: 2/3)
└── tests/
    └── stipendium_anspruch.yaml                  # YAML test cases
```

## Mapping legal text → code

| Legal section                                                   | OpenFisca artefact                                      |
| --------------------------------------------------------------- | ------------------------------------------------------- |
| Art. 12 Abs. 1, Art. 13 ABG — Stipendienrechtlicher Wohnsitz    | `hat_stipendienrechtlichen_wohnsitz_bern`               |
| Art. 12 Abs. 1 lit. b–d ABG — Persönlicher Status               | `erfuellt_persoenlichen_status`                         |
| Art. 6, 7 ABG — Anerkannte Ausbildung                           | `ausbildungstyp_anerkannt`                              |
| Art. 8 ABG — Anerkannte Ausbildungsstätte                       | `ausbildungsstaette_qualifiziert`                       |
| Art. 10 Abs. 1 ABG — Zweitausbildung nur Darlehen               | `stipendium_grundsaetzlich_ausgeschlossen`              |
| Art. 10 ABG — Volle vs. reduzierte Quote (Tertiär ≥ 4. Jahr)    | `stipendium_quote`                                      |
| Art. 15 Abs. 1 ABG — Bedürftigkeitsgrundsatz                    | `beduerftig`                                            |
| Art. 15 Abs. 2 ABG — Verzicht ab 25 / 4 J. Erwerbstätigkeit     | `verzicht_auf_anrechnung_eltern`                        |
| Art. 16 ABG — Fehlbetragsrechnung                               | `fehlbetrag`                                            |
| Art. 14 Abs. 1 ABG — Max. 12 Beitragsjahre                      | `maximale_beitragsdauer_eingehalten`                    |
| Art. 14 Abs. 4 ABG — Altersgrenze 35 J. + Ausnahmen             | `altersgrenze_eingehalten`                              |
| **Gesamtanspruch**                                              | **`stipendium_anspruch`**  →  **`stipendium_betrag`**   |

## Running the tests

```bash
openfisca test tests/ --country-package bern_stipendium
```

## Caveats

* The values for `eltern_quote_bei_verzicht` (50 %) and the citizenship sub-
  classes are best-effort placeholders; the ABV specifies the precise limits
  and should be consulted to fine-tune them.
* Art. 14 Abs. 5 ABG (no retroactive grants) is a *procedural* rule about
  filing the request and does not affect the eligibility formula — handled
  outside of OpenFisca by the authority's intake process.
* `maximale_beitragsdauer_eingehalten` checks `kumulierte_ausbildungsjahre <
  12`; the request year itself is intended to be excluded from that count
  (the count reflects past granting years).
