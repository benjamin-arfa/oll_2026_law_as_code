# Architecture — Law as Code

## Overview

This project uses a DSPy-based pipeline to transform Swiss federal legal text
(primarily the DFTA/AHV domain) into executable code targeting Catala or
OpenFisca. Legal articles are fetched from Fedlex via SPARQL, processed through
a language-model pipeline that generates structured code, and validated against
a suite of five Swiss test personas with known expected outcomes.

## Pipeline

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Fedlex      │     │  DSPy        │     │  Code        │     │  Validation  │
│  SPARQL      │────▶│  Pipeline    │────▶│  Generation  │────▶│  (Personas)  │
│  Fetcher     │     │  (CoT)       │     │  Catala /    │     │  5 test      │
│              │     │              │     │  OpenFisca   │     │  cases       │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │                     │
   fetch legal         transform to          produce              compare
   article text        structured repr.      executable code      against expected
   via SPARQL          with reasoning        from legal logic     AHV/tax values
```

## Components

### 1. Fedlex Fetcher (`fedlex.py`)

Queries the Fedlex SPARQL endpoint (`https://fedlex.data.admin.ch/sparqlendpoint`)
to retrieve Swiss federal legal articles. Targets the DFTA (Federal Act on the
Direct Federal Tax) and AHV (Old-Age and Survivors' Insurance) legislation.

- Input: article URI or classification code
- Output: structured legal text (German/French/Italian)
- Transport: `httpx` for async HTTP, `lxml` for XML/HTML parsing

### 2. DSPy Transformation Module (`pipeline.py`)

Uses DSPy signatures and modules to convert legal text into code:

- **`LegalToCode`** signature: `legal_article_text → catala_or_openfisca_code`
- **`LegalTransformer`** module: wraps `dspy.ChainOfThought` for step-by-step
  reasoning about the legal logic before generating code

### 3. Code Validator (planned)

Validates generated Catala/OpenFisca code by:
- Syntax checking (parse the output)
- Running the generated code against the persona test suite
- Comparing computed values to known expected results

## DSPy Training Loop

```
┌─────────────────────────────────────────────┐
│                Training Loop                │
│                                             │
│  1. Define Signature (LegalToCode)          │
│  2. Provide few-shot Examples               │
│     (data/examples/*.json)                  │
│  3. Build Module (LegalTransformer)         │
│  4. Choose Optimizer (BootstrapFewShot /    │
│     MIPROv2)                                │
│  5. Define Metric (persona test pass rate)  │
│  6. Compile & Evaluate                      │
│                                             │
│  Examples + Optimizer → Optimized Prompts   │
└─────────────────────────────────────────────┘
```

- **Signatures** define the input/output contract for the LM call
- **Examples** in `data/examples/` provide ground-truth pairs of legal text →
  code for few-shot learning
- **Optimizers** (e.g. `BootstrapFewShot`, `MIPROv2`) automatically select and
  order few-shot examples to maximize the metric
- **Metric**: percentage of personas whose computed AHV/tax values match
  expected results

## Validation — 5 Swiss Personas

| # | Persona   | Profile                        | Tests                          |
|---|-----------|--------------------------------|--------------------------------|
| 1 | Anna      | Single, employed, Zürich       | AHV contributions, income tax  |
| 2 | Beat      | Married, self-employed, Bern   | AHV contributions, deductions  |
| 3 | Clara     | Retired, Genève                | AHV pension calculation        |
| 4 | David     | Student, part-time, Basel      | AHV exemption threshold        |
| 5 | Elena     | Cross-border worker, Ticino    | AHV + international provisions |

Each persona has pre-computed expected values. The validation suite runs
generated code against all five personas and reports pass/fail per rule.
