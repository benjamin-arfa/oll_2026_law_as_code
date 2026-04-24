# Specification — OpenFisca as Code Generation Target

## 1. Decision Statement

We choose **OpenFisca** as the code generation target for the DSPy pipeline.

OpenFisca is the right fit for three reasons. First, it is **Python-native** — LLMs generate Python far more reliably than Catala's niche DSL syntax, which has almost no representation in training data. Second, its **structured formula pattern** (`Variable` subclass + `formula()` method) produces predictable, template-like code that DSPy can learn from few-shot examples. Third, its **built-in YAML testing** maps directly to our 5-persona validation suite, eliminating the need for a custom test harness.

---

## 2. Comparative Analysis

| Criterion                  | OpenFisca                                         | Catala                                            |
|----------------------------|---------------------------------------------------|---------------------------------------------------|
| **Language type**          | Python (standard library + NumPy vectorial ops)   | Custom DSL (`.catala_en` / `.catala_fr`)           |
| **Python interop**         | Native — classes inherit from `Variable`           | Requires compilation to Python via `catala`        |
| **Swiss law precedent**    | None yet, but country template allows bootstrapping| None; no known Swiss implementation                |
| **LLM generation reliability** | High — Python is the most-represented language in LLM training data | Very low — exotic syntax, tiny corpus, unreliable generation |
| **Testing framework**      | Built-in YAML test cases with dated parameters     | Ad-hoc; requires manual test scaffolding           |
| **Temporal versioning**    | First-class support via dated YAML parameters      | Supported in theory, but tooling is immature       |
| **Community maturity**     | Production deployments: France, UK, Tunisia, Senegal, Côte d'Ivoire | Academic; small community, unstable compiler       |
| **Formal verification**    | None built-in (runtime validation only)            | Designed for formal reasoning (theoretical advantage) |

**Bottom line:** Catala's formal-verification angle is theoretically appealing but practically unusable for our LLM-driven pipeline. OpenFisca gives us a battle-tested, Python-native framework that LLMs can target reliably.

### 2.1 Why Not Catala?

Catala is an academically rigorous language designed to let lawyers and developers co-author legislation as code, with built-in formal verification. In principle, it is the more elegant choice. In practice, five problems make it unworkable for this project:

1. **LLMs cannot write Catala reliably.** Catala's custom DSL syntax (scope declarations, context variables, `under condition ... consequence` blocks) barely exists in LLM training data. In our early experiments, models produced syntactically broken output the majority of the time. Python — the language OpenFisca uses — is the most-represented programming language in all major LLM training corpora, making generation far more consistent.

2. **Unstable compiler and toolchain.** The Catala compiler is still under active academic development. Breaking changes between releases, sparse documentation, and platform-specific build issues (especially on macOS/ARM) create friction that would slow the project significantly.

3. **Tiny community, minimal support.** Catala's user base is almost entirely within the Inria research group and a handful of academic collaborators. When something breaks, there is no Stack Overflow thread, no Discord community of practitioners, and no production deployment to reference. OpenFisca, by contrast, has active deployments in France (mes-aides.gouv.fr), the UK, Tunisia, Senegal, and Côte d'Ivoire, with an established community and issue tracker.

4. **No bootstrapping path for Switzerland.** OpenFisca provides an official [country template](https://github.com/openfisca/country-template) with a well-documented process for defining entities, parameters, and variables for a new jurisdiction. Catala has no equivalent — building a Swiss law package would mean starting from a blank file with no structural guidance.

5. **Testing requires a custom harness.** OpenFisca's YAML test format (`input` / `output` / `period`) maps directly to our 5-persona validation suite. With Catala, we would need to build a bespoke test runner that compiles `.catala_en` to Python, executes it, and compares results — adding an entire layer of tooling that contributes nothing to the research goal.

**What we lose:** Catala's formal-verification capability — the ability to mathematically prove that code faithfully represents the law — is a genuine and unique advantage. However, that advantage is irrelevant if the LLM cannot generate valid Catala in the first place. Should the Catala ecosystem mature and LLM support improve, revisiting this decision would be worthwhile.

---

## 3. OpenFisca Code Patterns for AHV

The following examples show what the DSPy pipeline should generate for AHV (Old-Age and Survivors' Insurance) rules.

### 3.1 Variable with Formula — Employee AHV Contribution

```python
from openfisca_core.model_api import *
from openfisca_switzerland.entities import Person


class ahv_employee_contribution(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "AHV/IV/EO employee contribution (Art. 5 AHVG)"

    def formula(person, period, parameters):
        gross_salary = person("gross_monthly_salary", period)
        rate = parameters(period).social_security.ahv.employee_rate
        return gross_salary * rate
```

### 3.2 Parameter YAML — Dated AHV Rates

```yaml
# parameters/social_security/ahv/employee_rate.yaml
description: AHV/IV/EO employee contribution rate (Art. 5 AHVG)
metadata:
  unit: /1
  reference:
    - title: "AHVG Art. 5 — Beiträge von Einkommen aus unselbständiger Erwerbstätigkeit"
      href: "https://www.fedlex.admin.ch/eli/cc/63/837_843_843/de#art_5"
values:
  2024-01-01:
    value: 0.0435
  2020-01-01:
    value: 0.0425
  1997-01-01:
    value: 0.0415
```

### 3.3 Persona YAML Test Case — Anna

```yaml
# tests/anna_ahv.yaml
- name: "Anna — employed, Zürich, CHF 85'000 annual income"
  period: 2024-01
  input:
    gross_monthly_salary: 7083.33  # CHF 85'000 / 12
  output:
    ahv_employee_contribution: 308.12  # 7083.33 * 0.0435
```

---

## 4. DSPy Pipeline Integration

### 4.1 Updated Signature

The `LegalToCode` signature produces OpenFisca-specific outputs:

| Field                   | Direction | Description                                                        |
|-------------------------|-----------|--------------------------------------------------------------------|
| `legal_article_text`    | Input     | Full text of a Swiss federal legal article (DE/FR/IT)              |
| `article_reference`     | Input     | Article identifier, e.g. `AHVG Art. 5`                            |
| `openfisca_variable`    | Output    | Python class code — a `Variable` subclass with `formula()`        |
| `parameter_yaml`        | Output    | YAML snippet defining rates/thresholds with dated values           |
| `reasoning`             | Output    | Step-by-step explanation of how the legal text maps to the code    |

### 4.2 Generation Flow

```
legal_article_text + article_reference
        │
        ▼
┌─────────────────────────────┐
│  DSPy ChainOfThought        │
│  (LegalToCode signature)    │
│                             │
│  1. Identify legal rule     │
│  2. Extract parameters      │
│  3. Map to OpenFisca pattern│
│  4. Generate Variable class │
│  5. Generate parameter YAML │
└─────────────────────────────┘
        │
        ▼
openfisca_variable  +  parameter_yaml  +  reasoning
```

### 4.3 Few-Shot Example Strategy

Each few-shot example provided to the DSPy optimizer consists of:

1. **Input:** The German text of a specific AHV article (e.g. AHVG Art. 5)
2. **Output:** The corresponding OpenFisca `Variable` class + parameter YAML
3. **Reasoning:** A step-by-step walkthrough of the legal-to-code mapping

The `BootstrapFewShot` optimizer selects and orders these examples to maximize the persona test pass rate metric.

---

## 5. Risks & Mitigations

| Risk                                        | Likelihood | Impact | Mitigation                                                                                  |
|---------------------------------------------|------------|--------|---------------------------------------------------------------------------------------------|
| No `openfisca-switzerland` package exists    | Certain    | High   | Bootstrap from the official [country template](https://github.com/openfisca/country-template); define Swiss entities (`Person`, `Household`, `Canton`) and core parameters |
| Vectorial NumPy patterns are unusual for LLMs | Medium    | Medium | Provide few-shot examples that explicitly demonstrate the `person("variable", period)` pattern; constrain output with DSPy assertions |
| AHV rules reference multiple articles        | High       | Medium | Support multi-variable generation: one DSPy call can produce several `Variable` classes that reference each other via `person("other_variable", period)` |
| OpenFisca's dated parameters require exact formatting | Medium | Low | Include parameter YAML templates in the few-shot examples; validate YAML structure post-generation |
| Generated code may not parse or run          | Medium     | High   | Add a syntax-check step after generation (import the class, instantiate a `TaxBenefitSystem`, run a smoke test) before persona validation |
