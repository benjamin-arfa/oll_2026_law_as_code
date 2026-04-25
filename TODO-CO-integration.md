# TODO: CO (Code of Obligations) Integration for OpenFisca Code Generation

> **Purpose:** Complete, self-contained instructions for a scheduled Claude job to extend the DSPy pipeline from AHVG-only to full CO (Code of Obligations) support.
>
> **Branch:** `feat/OR-integration`
>
> **Key principle:** CO law produces boolean determinations (is there liability? is the contract null?), not numeric calculations. The pipeline must learn these patterns through new training examples, improved metrics, and specialized DSPy skills.

---

## Prerequisites / Context

- The DSPy pipeline lives in `src/oll_law_as_code/pipeline.py` — `LegalToCode` signature + `LegalTransformer` module (ChainOfThought)
- Optimized module: `data/optimized/legal_transformer.json` (3 AHVG demos)
- Current training examples: `data/examples/*.yaml` (4 AHVG + 1 OR Art. 41 = 5 total)
- CO wiki: `data/legal texts/wiki-CO/` — systematic legal framework (Chappuis & Marchand, Univ. Geneva 2021)
- The critical document is `data/legal texts/wiki-CO/pretentions/execution.md` — the "keys for judgement" decision tree
- Reference implementation for boolean legal logic: `src/bern_stipendium/variables/eligibility.py` — shows the exact OpenFisca pattern (composed boolean variables with exclusions via `(1 - var)`)
- Legal text language: use **French** (matches the wiki-CO source and academic precision)

---

## TODO 1: Add ~42 CO boolean input variables to OpenFisca country package

**File to edit:** `src/openfisca_switzerland/variables/inputs.py`

**What:** Append CO-specific input variables below the existing 5 AHVG variables (`gross_monthly_salary`, `self_employment_income`, `age`, `has_swiss_residence`, `has_swiss_employment`). Keep existing variables untouched.

**How:** Each variable is a `Variable` subclass with no `formula`, using the same pattern as the existing ones. Group by domain with comment headers.

### 1a. Tort Liability inputs (CO 41) — MUST ADD FIRST (already referenced by existing `or_art41_tort_liability.yaml` but never defined)

```python
# ===========================================================================
# CO Art. 41 — Responsabilité délictuelle (Tort Liability)
# ===========================================================================

class has_unlawful_act(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "An unlawful act has been committed (CO 41)"
    default_value = False

class has_damage(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "The plaintiff has suffered damage (CO 41, 45, 46)"
    default_value = False

class has_causation(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Adequate causal link between act and damage (CO 41)"
    default_value = False

class has_intent(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "The defendant acted intentionally (CO 41)"
    default_value = False

class has_negligence(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "The defendant acted negligently (CO 41)"
    default_value = False

class is_contrary_to_morals(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "The act is contrary to public morals (CO 41 II)"
    default_value = False
```

### 1b. Contract Formation inputs (CO 1-9)

```python
# ===========================================================================
# CO Art. 1-9 — Formation du contrat (Contract Formation)
# ===========================================================================

class has_offer(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "An offer (offre) has been made (CO 1)"
    default_value = False

class has_acceptance(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "An acceptance (acceptation) has been communicated (CO 1)"
    default_value = False

class has_concordance(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Offer and acceptance concord in meaning (principle of trust, CO 1-2)"
    default_value = False

class has_reciprocity(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Offer was addressed to acceptor and acceptance to offeror (CO 1)"
    default_value = False

class has_required_form(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Required form has been observed (CO 11 ss), or no form required"
    default_value = True

class has_capacity(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Parties have capacity to contract (CC 12 ss)"
    default_value = True
```

### 1c. Contract Nullity inputs (CO 20)

```python
# ===========================================================================
# CO Art. 20 — Nullité du contrat (Contract Nullity)
# ===========================================================================

class has_impossible_object(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Contract has an impossible object (CO 20 I, 1st hypothesis)"
    default_value = False

class has_illicit_object(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Contract has an illicit object or purpose (CO 20 I, 2nd hypothesis)"
    default_value = False

class has_immoral_object(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Contract is contrary to public morals (CO 20 I, 3rd hypothesis)"
    default_value = False

class has_form_defect(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Contract violates a mandatory form requirement (CO 11 ss)"
    default_value = False
```

### 1d. Contractual Liability inputs (CO 97)

```python
# ===========================================================================
# CO Art. 97 — Responsabilité contractuelle (Contractual Liability)
# ===========================================================================

class has_contractual_obligation(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "A contractual obligation exists between the parties"
    default_value = False

class has_breach_of_obligation(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "The defendant has breached a contractual obligation (CO 97)"
    default_value = False

class has_contractual_damage(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Plaintiff has suffered damage from breach of positive interest (CO 97)"
    default_value = False

class has_adequate_causation(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "There is an adequate causal link between breach and damage"
    default_value = False

class has_presumed_fault(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Fault is presumed (CO 97: presumption of fault for contractual liability)"
    default_value = True
```

### 1e. Unjust Enrichment inputs (CO 62)

```python
# ===========================================================================
# CO Art. 62 — Enrichissement illégitime (Unjust Enrichment)
# ===========================================================================

class has_enrichment(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "The defendant has been enriched (CO 62)"
    default_value = False

class has_impoverishment(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "The plaintiff has been impoverished (CO 62)"
    default_value = False

class has_connexity(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Enrichment and impoverishment are connected (CO 62)"
    default_value = False

class has_no_legal_basis(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "The enrichment lacks a legal basis / cause (CO 62)"
    default_value = False
```

### 1f. Prescription inputs (CO 127-128)

```python
# ===========================================================================
# CO Art. 127-128 — Prescription
# ===========================================================================

class claim_age_years(Variable):
    value_type = int
    entity = Person
    definition_period = YEAR
    label = "Age of the claim in years (since the claim became due)"
    default_value = 0

class is_periodic_claim(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "The claim is a periodic obligation (rent, interest, salary) per CO 128"
    default_value = False
```

### 1g. Employer Liability inputs (CO 55)

```python
# ===========================================================================
# CO Art. 55 — Responsabilité de l'employeur (Employer Liability)
# ===========================================================================

class is_employer_of_tortfeasor(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "The defendant is the employer of the person who committed the tort (CO 55)"
    default_value = False

class employee_committed_tort(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "The employee committed an unlawful act (CO 55, CO 41)"
    default_value = False

class tort_in_course_of_employment(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "The tort was committed in the course of employment (CO 55)"
    default_value = False

class employer_proves_diligence(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Employer proves due diligence in selection, instruction, and supervision (CO 55 triple proof)"
    default_value = False
```

### 1h. Debtor Default inputs (CO 102-107)

```python
# ===========================================================================
# CO Art. 102-107 — Demeure du débiteur (Debtor Default)
# ===========================================================================

class obligation_is_due(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "The contractual obligation is due and exigible (CO 75 ss)"
    default_value = False

class debtor_has_been_summoned(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Debtor has been put in default by interpellation (CO 102 I) or fixed term (CO 102 II)"
    default_value = False

class additional_delay_granted(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "An additional delay has been granted to the debtor (CO 107 I)"
    default_value = False

class debtor_failed_to_perform(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Debtor has still not performed after the additional delay (CO 107)"
    default_value = False
```

### 1i. Warranty inputs (CO 197-210)

```python
# ===========================================================================
# CO Art. 197-210 — Garantie pour les défauts (Warranty)
# ===========================================================================

class has_sale_or_work_contract(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "A valid contract of sale or work exists (CO 184 ss / CO 363 ss)"
    default_value = False

class has_defect(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "The thing delivered or the work has a defect (CO 197)"
    default_value = False

class defect_before_risk_transfer(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "The defect existed before transfer of risk (CO 185)"
    default_value = False

class buyer_unaware_of_defect(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Buyer was unaware of the defect at time of contract (CO 200)"
    default_value = False

class timely_notice_of_defect(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Notice of defect was given in a timely manner (CO 201)"
    default_value = False

class defect_reduction_amount(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Amount of price reduction due to defect (Minderung, CO 205 I)"
    default_value = 0.0

class purchase_price(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Original purchase price of the thing sold"
    default_value = 0.0
```

### Verification for TODO 1

```bash
python -c "from openfisca_switzerland import CountryTaxBenefitSystem; CountryTaxBenefitSystem()"
```
Must load without errors.

---

## TODO 2: Create 8 CO training examples in `data/examples/`

**Template:** Use `data/examples/or_art41_tort_liability.yaml` as the structural reference. Each YAML file must have these top-level keys: `legal_article_text` (multiline `|`), `article_reference` (string), `openfisca_variable` (multiline `|` with Python code), `parameter_yaml` (multiline `|`), `reasoning` (multiline `|`).

**Language:** Use French legal text from the CO wiki / CO.xml.

### 2a. `data/examples/or_art1_contract_formation.yaml`

- **Reference:** `"OR Art. 1"`
- **Legal text:** Art. 1 CO — "Le contrat est parfait lorsque les parties ont, réciproquement et d'une manière concordante, manifesté leur volonté. Cette manifestation peut être expresse ou tacite."
- **Variable name:** `or_contract_formation`
- **value_type:** bool, Person, YEAR
- **Formula logic:** ALL conditions must be met (conjunctive AND):
  ```python
  has_offer * has_acceptance * has_concordance * has_reciprocity * has_required_form * has_capacity > 0
  ```
- **Parameter YAML:** Reference-only (no numeric values), dated `1912-01-01`
- **Reasoning should explain:** Contract formation requires offer (CO 1) + acceptance (CO 1) + concordance (principle of trust) + reciprocity + form (CO 11 ss) + capacity (CC 12 ss). Source: `wiki-CO/pretentions/execution.md` lines 15-69.

### 2b. `data/examples/or_art20_contract_nullity.yaml`

- **Reference:** `"OR Art. 20"`
- **Legal text:** Art. 20 CO — "Le contrat est nul s'il a pour objet une chose impossible, illicite ou contraire aux mœurs."
- **Variable name:** `or_contract_nullity`
- **value_type:** bool, Person, YEAR
- **Formula logic:** ANY ground suffices (disjunctive OR):
  ```python
  has_impossible_object + has_illicit_object + has_immoral_object + has_form_defect > 0
  ```
- **Parameter YAML:** Reference-only, dated `1912-01-01`
- **Reasoning should explain:** Art. 20 I lists three grounds for nullity (impossible, illicit, immoral). Form defects (CO 11 ss) are an additional ground. Any single ground suffices to render the contract null. Source: `wiki-CO/pretentions/execution.md` lines 174-196.

### 2c. `data/examples/or_art97_contractual_liability.yaml`

- **Reference:** `"OR Art. 97"`
- **Legal text:** Art. 97 CO — "Lorsque le créancier ne peut obtenir l'exécution de l'obligation ou ne peut l'obtenir qu'imparfaitement, le débiteur est tenu de réparer le dommage en résultant, à moins qu'il ne prouve qu'aucune faute ne lui est imputable."
- **Variable name:** `or_contractual_liability`
- **value_type:** bool, Person, YEAR
- **Formula logic:** Conjunctive with PRESUMED fault:
  ```python
  has_contractual_obligation * has_breach_of_obligation * has_contractual_damage * has_adequate_causation * has_presumed_fault > 0
  ```
- **KEY INSIGHT for reasoning:** `has_presumed_fault` defaults to `True` because fault is PRESUMED under CO 97. The defendant must prove absence of fault to escape liability (reversed burden of proof). This is the fundamental difference from delictual liability (CO 41) where fault must be proven.
- **Parameter YAML:** Reference-only, dated `1912-01-01`
- **Source logic:** `wiki-CO/pretentions/dommages-interets.md` lines 8-66.

### 2d. `data/examples/or_art62_unjust_enrichment.yaml`

- **Reference:** `"OR Art. 62"`
- **Legal text:** Art. 62 CO — "Celui qui, sans cause légitime, s'est enrichi aux dépens d'autrui, est tenu à restitution."
- **Variable name:** `or_unjust_enrichment`
- **value_type:** bool, Person, YEAR
- **Formula logic:** All 4 conjunctive conditions:
  ```python
  has_enrichment * has_impoverishment * has_connexity * has_no_legal_basis > 0
  ```
- **Parameter YAML:** Reference-only, dated `1912-01-01`
- **Reasoning:** 4 cumulative conditions from CO 62: enrichment of defendant + impoverishment of plaintiff + connexity between them + absence of legal basis. Source: `wiki-CO/pretentions/restitution.md` lines 129-173.

### 2e. `data/examples/or_art127_prescription.yaml`

- **Reference:** `"OR Art. 127-128"`
- **Legal text:** Art. 127 — "Toutes les actions se prescrivent par dix ans..." + Art. 128 — "Se prescrivent par cinq ans: les loyers et fermages, les intérêts de capitaux et toutes autres redevances périodiques..."
- **Variable name:** `or_claim_prescribed`
- **value_type:** bool, Person, YEAR
- **Formula logic:** Two paths with numeric thresholds:
  ```python
  is_periodic_claim * (claim_age_years >= parameters(period).obligations.prescription.periodic_years) + (1 - is_periodic_claim) * (claim_age_years >= parameters(period).obligations.prescription.general_years) > 0
  ```
- **Parameter YAML:** Store actual thresholds (not just references):
  ```yaml
  description: Prescription periods (Art. 127-128 CO)
  metadata:
    reference:
      - title: "CO Art. 127 — Prescription ordinaire"
        href: "https://www.fedlex.admin.ch/eli/cc/27/317_321_377/fr#art_127"
  obligations:
    prescription:
      general_years:
        values:
          1912-01-01:
            value: 10
      periodic_years:
        values:
          1912-01-01:
            value: 5
  ```
- **Source logic:** `wiki-CO/pretentions/execution.md` lines 330-338.

### 2f. `data/examples/or_art55_employer_liability.yaml`

- **Reference:** `"OR Art. 55"`
- **Legal text:** Art. 55 CO — "L'employeur est responsable du dommage causé par ses travailleurs ou ses autres auxiliaires dans l'accomplissement de leur travail, s'il ne prouve qu'il a pris tous les soins commandés par les circonstances..."
- **Variable name:** `or_employer_liability`
- **value_type:** bool, Person, YEAR
- **Formula logic:** Conjunctive conditions + defense via negation:
  ```python
  is_employer_of_tortfeasor * employee_committed_tort * tort_in_course_of_employment * has_damage * has_causation * (1 - employer_proves_diligence) > 0
  ```
- **KEY INSIGHT for reasoning:** The "triple proof of diligence" (cura in eligendo, in instruendo, in custodiendo) is modeled as a DEFENSE via `(1 - employer_proves_diligence)`. Same pattern as `(1 - person("stipendium_grundsaetzlich_ausgeschlossen", period))` in `src/bern_stipendium/variables/eligibility.py:258`. The `employer_proves_diligence` defaults to `False`, so liability is the default unless the employer proves otherwise.
- **Parameter YAML:** Reference-only, dated `1912-01-01`
- **Source logic:** `wiki-CO/pretentions/dommages-interets.md` lines 438-456.

### 2g. `data/examples/or_art102_debtor_default.yaml`

- **Reference:** `"OR Art. 102"`
- **Legal text:** Art. 102 CO — "Le débiteur d'une obligation exigible est mis en demeure par l'interpellation du créancier."
- **Variable name:** `or_debtor_in_default`
- **value_type:** bool, Person, YEAR
- **Formula logic:** Sequential conditions (all must hold):
  ```python
  obligation_is_due * debtor_has_been_summoned * debtor_failed_to_perform > 0
  ```
- **Parameter YAML:** Reference-only, dated `1912-01-01`
- **Reasoning:** Debtor default requires: (1) obligation is due and exigible (CO 75 ss), (2) debtor has been summoned / interpellated (CO 102 I) or fixed term expired (CO 102 II), (3) debtor still hasn't performed. Source: `wiki-CO/pretentions/execution.md` lines 219, 258-260.

### 2h. `data/examples/or_art197_warranty_claims.yaml`

- **Reference:** `"OR Art. 197"`
- **Legal text:** Art. 197 CO — "Le vendeur est tenu de garantir l'acheteur tant en raison des qualités promises qu'en raison des défauts qui, matériellement ou juridiquement, enlèvent à la chose soit sa valeur, soit son utilité prévue, ou qui les diminuent dans une notable mesure."
- **Variable name:** `or_warranty_claim_valid`
- **value_type:** bool, Person, YEAR
- **Formula logic:** All conditions from actions édiliciennes:
  ```python
  has_sale_or_work_contract * has_defect * defect_before_risk_transfer * buyer_unaware_of_defect * timely_notice_of_defect > 0
  ```
- **Parameter YAML:** Reference-only, dated `1912-01-01`
- **Reasoning:** Warranty claims require 5 cumulative conditions from the actions édiliciennes framework: (1) valid sale/work contract, (2) defect in the thing, (3) defect existed before risk transfer (CO 185), (4) buyer unaware of defect at contract time (CO 200), (5) timely notice of defect (CO 201). Source: `wiki-CO/pretentions/dommages-interets.md` lines 185-224.

### Verification for TODO 2

```bash
python -c "from oll_law_as_code.examples import make_examples; print(len(make_examples()))"
```
Must print `13` (5 existing + 8 new).

---

## TODO 3: Improve metric and runner for boolean CO outputs

### 3a. Update default smoke-test inputs in runner.py

**File:** `src/oll_law_as_code/runner.py`

In the default `input_data` dict (around line 69-73), add CO boolean inputs so that boolean variables get `True` inputs and don't silently produce default `False` (which gives misleading partial credit):

```python
if input_data is None:
    input_data = {
        "persons": {
            "p1": {
                "gross_monthly_salary": {period: 7083.33},
                # CO boolean defaults for smoke-testing
                "has_offer": {period: True},
                "has_acceptance": {period: True},
                "has_concordance": {period: True},
                "has_reciprocity": {period: True},
                "has_unlawful_act": {period: True},
                "has_damage": {period: True},
                "has_causation": {period: True},
                "has_intent": {period: True},
            },
        },
        "households": {"h1": {"parents": ["p1"]}},
    }
```

### 3b. Improve metric boolean handling in metric.py

**File:** `src/oll_law_as_code/metric.py`

**Change 1:** Add a 5th structural check for `value_type = bool`. Redistribute the 0.25 pts across 5 checks (0.05 each instead of 0.0625 each):

```python
# --- Structural checks (0.05 each, total 0.25) ---
if re.search(r"class\s+\w+\(Variable\)", code):
    score += 0.05
if "def formula(" in code:
    score += 0.05
if "definition_period" in code:
    score += 0.05
if re.search(r"\d{4}-\d{2}-\d{2}", yaml_text):
    score += 0.05
if re.search(r"value_type\s*=\s*(bool|float|int)", code):
    score += 0.05
```

**Change 2:** In Tier 2 value matching (line 96-99), add exact boolean comparison alongside the existing numeric tolerance:

```python
if expected_code and result.computed_values:
    if re.search(r"value_type\s*=\s*bool", code):
        # Boolean: check that at least one computed value is True
        for var_name, vals in result.computed_values.items():
            if any(v in (True, 1, 1.0) for v in (vals if hasattr(vals, '__iter__') else [vals])):
                score += 0.15
                break
    else:
        # Numeric: existing 1% tolerance check
        score += 0.15
```

### Verification for TODO 3

```bash
python -c "from oll_law_as_code.metric import code_quality_metric; print('metric ok')"
```

---

## TODO 4: Create specialized DSPy skills

### 4a. Create `src/oll_law_as_code/skills.py`

Three specialized DSPy signatures for different CO legal patterns:

```python
"""Specialized DSPy signatures for different legal pattern types in CO."""

import dspy


class BooleanDetermination(dspy.Signature):
    """Transform a Swiss legal article into a boolean determination variable.

    The article defines conditions for a legal determination (yes/no).
    Produce a Python Variable class with value_type = bool and a formula
    that combines boolean input variables using AND/OR logic.
    """
    legal_article_text: str = dspy.InputField(
        desc="Full text of a Swiss legal article defining conditions for a legal determination"
    )
    article_reference: str = dspy.InputField(
        desc="Article identifier, e.g. 'OR Art. 20' or 'OR Art. 97'"
    )
    available_variables: str = dspy.InputField(
        desc="Already-defined OpenFisca variables that may be referenced",
        default="",
    )
    legal_pattern: str = dspy.InputField(
        desc="Type of legal pattern: 'conjunctive' (all conditions required), 'disjunctive' (any condition suffices), or 'layered' (conditions + objections + exceptions)",
        default="conjunctive",
    )
    openfisca_variable: str = dspy.OutputField(
        desc="Python class with value_type = bool implementing boolean determination logic"
    )
    parameter_yaml: str = dspy.OutputField(
        desc="YAML snippet — typically reference-only for boolean determinations"
    )
    reasoning: str = dspy.OutputField(
        desc="Step-by-step explanation mapping legal conditions to boolean algebra"
    )


class LayeredClaimAnalysis(dspy.Signature):
    """Transform a Swiss legal claim structure into executable code.

    Swiss law uses a layered analysis: CONDITIONS (all must hold) then
    OBJECTIONS (any defeats the claim) then EXCEPTIONS (any also defeats).
    The formula pattern is:
        conditions_met AND NOT any_objection AND NOT any_exception
    """
    legal_article_text: str = dspy.InputField(
        desc="Full text of the main legal article(s)"
    )
    article_reference: str = dspy.InputField(
        desc="Article identifier"
    )
    available_variables: str = dspy.InputField(
        desc="Already-defined OpenFisca variables",
        default="",
    )
    conditions_summary: str = dspy.InputField(
        desc="Summary of the positive conditions that must be met for the claim"
    )
    objections_summary: str = dspy.InputField(
        desc="Summary of objections that defeat the claim (e.g., nullity, prescription)"
    )
    exceptions_summary: str = dspy.InputField(
        desc="Summary of exceptions that defeat the claim (e.g., compensation, novation)"
    )
    openfisca_variable: str = dspy.OutputField(
        desc="Python class implementing layered claim logic: conditions * (1 - objections) * (1 - exceptions)"
    )
    parameter_yaml: str = dspy.OutputField(
        desc="YAML parameter snippet"
    )
    reasoning: str = dspy.OutputField(
        desc="Step-by-step analysis following conditions > objections > exceptions"
    )


class CrossReferenceResolution(dspy.Signature):
    """Transform a legal article that heavily references other articles.

    The article delegates part of its logic to other articles. The generated
    code should call person("other_variable", period) for each referenced
    article that has already been coded.
    """
    legal_article_text: str = dspy.InputField(
        desc="Full text of the legal article with cross-references"
    )
    article_reference: str = dspy.InputField(
        desc="Article identifier"
    )
    available_variables: str = dspy.InputField(
        desc="Already-defined OpenFisca variables that can be referenced"
    )
    referenced_articles: str = dspy.InputField(
        desc="List of referenced article identifiers and what they determine"
    )
    openfisca_variable: str = dspy.OutputField(
        desc="Python class that delegates to existing variables via person() calls"
    )
    parameter_yaml: str = dspy.OutputField(
        desc="YAML parameter snippet"
    )
    reasoning: str = dspy.OutputField(
        desc="Explanation of which references are resolved and how"
    )
```

### 4b. Create `src/oll_law_as_code/skill_transformer.py`

A `SkillRouter` that classifies articles and routes to the right ChainOfThought skill:

```python
"""Skill-aware DSPy module that selects the right signature for each legal pattern."""

import dspy

from oll_law_as_code.pipeline import LegalToCode
from oll_law_as_code.skills import (
    BooleanDetermination,
    LayeredClaimAnalysis,
    CrossReferenceResolution,
)


class SkillRouter(dspy.Signature):
    """Classify a legal article to determine which transformation skill to use."""
    legal_article_text: str = dspy.InputField(desc="Full text of a Swiss legal article")
    article_reference: str = dspy.InputField(desc="Article identifier")
    skill: str = dspy.OutputField(
        desc="One of: 'numeric_calculation', 'boolean_determination', 'layered_claim', 'cross_reference'"
    )
    pattern_hints: str = dspy.OutputField(
        desc="Brief description of the legal pattern detected"
    )


class SkillAwareTransformer(dspy.Module):
    """Routes legal articles to the appropriate specialized transformation skill."""

    def __init__(self):
        super().__init__()
        self.router = dspy.Predict(SkillRouter)
        self.general = dspy.ChainOfThought(LegalToCode)
        self.boolean = dspy.ChainOfThought(BooleanDetermination)
        self.layered = dspy.ChainOfThought(LayeredClaimAnalysis)
        self.cross_ref = dspy.ChainOfThought(CrossReferenceResolution)

    def forward(self, legal_article_text: str, article_reference: str,
                available_variables: str = "", **kwargs):
        route = self.router(
            legal_article_text=legal_article_text,
            article_reference=article_reference,
        )
        skill = route.skill.strip().lower()

        if skill == "boolean_determination":
            return self.boolean(
                legal_article_text=legal_article_text,
                article_reference=article_reference,
                available_variables=available_variables,
                legal_pattern=kwargs.get("legal_pattern", "conjunctive"),
            )
        elif skill == "layered_claim":
            return self.layered(
                legal_article_text=legal_article_text,
                article_reference=article_reference,
                available_variables=available_variables,
                conditions_summary=kwargs.get("conditions_summary", ""),
                objections_summary=kwargs.get("objections_summary", ""),
                exceptions_summary=kwargs.get("exceptions_summary", ""),
            )
        elif skill == "cross_reference":
            return self.cross_ref(
                legal_article_text=legal_article_text,
                article_reference=article_reference,
                available_variables=available_variables,
                referenced_articles=kwargs.get("referenced_articles", ""),
            )
        else:
            return self.general(
                legal_article_text=legal_article_text,
                article_reference=article_reference,
                available_variables=available_variables,
            )
```

### Verification for TODO 4

```bash
python -c "from oll_law_as_code.skills import BooleanDetermination, LayeredClaimAnalysis, CrossReferenceResolution; print('skills ok')"
python -c "from oll_law_as_code.skill_transformer import SkillAwareTransformer; print('skill_transformer ok')"
```

---

## TODO 5: Add CO personas for validation

### 5a. Extend Persona dataclass and add CO personas

**File:** `src/oll_law_as_code/personas.py`

**Change 1:** Add `extra_inputs` field to the `Persona` dataclass:
```python
extra_inputs: dict[str, dict[str, bool | int | float]] = field(default_factory=dict)
```

**Change 2:** Add 3 new CO personas after `ELENA`:

```python
FRANCOIS = Persona(
    name="Francois",
    age=50,
    canton="GE",
    employment_status="employed",
    marital_status="married",
    annual_income=Decimal("150000"),
    description="Employer in Geneva whose employee caused a tort — tests CO 55 employer liability",
    expected_values={
        "or_employer_liability": Decimal("1"),  # True
    },
    extra_inputs={
        "is_employer_of_tortfeasor": {"2024": True},
        "employee_committed_tort": {"2024": True},
        "tort_in_course_of_employment": {"2024": True},
        "has_damage": {"2024": True},
        "has_causation": {"2024": True},
        "employer_proves_diligence": {"2024": False},
    },
)

GIULIA = Persona(
    name="Giulia",
    age=30,
    canton="VD",
    employment_status="employed",
    marital_status="single",
    annual_income=Decimal("70000"),
    description="Buyer of defective goods in Vaud — tests CO 197 warranty claims",
    expected_values={
        "or_warranty_claim_valid": Decimal("1"),  # True
    },
    extra_inputs={
        "has_sale_or_work_contract": {"2024": True},
        "has_defect": {"2024": True},
        "defect_before_risk_transfer": {"2024": True},
        "buyer_unaware_of_defect": {"2024": True},
        "timely_notice_of_defect": {"2024": True},
    },
)

HANS = Persona(
    name="Hans",
    age=55,
    canton="ZH",
    employment_status="self_employed",
    marital_status="divorced",
    annual_income=Decimal("200000"),
    description="Contractor in Zurich with overdue payment — tests CO 102 debtor default",
    expected_values={
        "or_debtor_in_default": Decimal("1"),  # True
    },
    extra_inputs={
        "obligation_is_due": {"2024": True},
        "debtor_has_been_summoned": {"2024": True},
        "debtor_failed_to_perform": {"2024": True},
    },
)
```

**Change 3:** Update `ALL_PERSONAS`:
```python
ALL_PERSONAS = [ANNA, BEAT, CLARA, DAVID, ELENA, FRANCOIS, GIULIA, HANS]
```

### 5b. Update persona_runner.py to merge extra_inputs

**File:** `src/oll_law_as_code/persona_runner.py`

In `persona_to_openfisca_input`, after building the `person_data` dict, merge `extra_inputs`:

```python
for var_name, period_values in persona.extra_inputs.items():
    person_data[var_name] = period_values
```

---

## TODO 6: Update reference extraction regex for CO patterns

**File:** `src/oll_law_as_code/references.py`

The CO wiki uses shorthand like `CO 20`, `CO 97`, `CO 127` (without "Art."). Add a second regex pattern:

```python
_CO_SHORT_RE = re.compile(
    r"(?:CO|OR)\s+(\d+)",  # "CO 20", "OR 41"
    re.IGNORECASE,
)
```

Update `extract_references()` to also scan for `_CO_SHORT_RE` matches, normalizing them to the standard format (e.g., `CO 20` → `OR Art. 20`).

---

## TODO 7: Re-optimize the module with expanded training set

**File:** `optimize.py`

After TODOs 1-2 are complete (training set grows from 5 → 13 examples), update the optimization parameters:

```python
optimizer = dspy.BootstrapFewShot(
    metric=code_quality_metric,
    max_bootstrapped_demos=4,    # was 2 — now captures both AHVG and CO patterns
    max_labeled_demos=5,          # was 3
    max_rounds=2,                 # was 1
)
```

Run `python optimize.py` — saves to `data/optimized/legal_transformer.json`.

---

## TODO 8: Create CO validation script and evaluate

### 8a. Create `run_co.py` in the project root

Test OR Art. 20 (nullity) end-to-end:

```python
"""Run CO article transformation and validate."""
import os
from pathlib import Path
from dotenv import load_dotenv
import dspy

from oll_law_as_code.pipeline import LegalTransformer
from oll_law_as_code.runner import run_generated_code

OR_ART_20 = """\
Art. 20 — Nullité

1 Le contrat est nul s'il a pour objet une chose impossible, illicite ou \
contraire aux mœurs.

2 Si le contrat n'est vicié que dans certaines de ses clauses, ces clauses \
sont seules frappées de nullité, à moins qu'il n'y ait lieu d'admettre que \
le contrat n'aurait pas été conclu sans elles.\
"""

def main():
    load_dotenv()
    lm = dspy.LM(
        "cerebras/qwen-3-235b-a22b-instruct-2507",
        api_key=os.environ["CEREBRAS_API_KEY"],
    )
    dspy.configure(lm=lm)

    transformer = LegalTransformer()
    optimized_path = Path("data/optimized/legal_transformer.json")
    if optimized_path.exists():
        transformer.load(optimized_path)

    result = transformer(
        legal_article_text=OR_ART_20,
        article_reference="OR Art. 20",
    )

    print("=== Generated Code ===")
    print(result.openfisca_variable)
    print("\n=== Generated YAML ===")
    print(result.parameter_yaml)
    print("\n=== Reasoning ===")
    print(result.reasoning)

    # Test with a null contract scenario (illicit object)
    test_input = {
        "persons": {"p1": {
            "has_illicit_object": {"2024": True},
            "has_impossible_object": {"2024": False},
            "has_immoral_object": {"2024": False},
            "has_form_defect": {"2024": False},
        }},
        "households": {"h1": {"parents": ["p1"]}},
    }

    exec_result = run_generated_code(
        result.openfisca_variable,
        result.parameter_yaml,
        input_data=test_input,
        period="2024",
    )

    if exec_result.success:
        print(f"\nExecution SUCCESS: {exec_result.computed_values}")
        # Expected: or_contract_nullity = True (1.0) because has_illicit_object is True
    else:
        print(f"\nExecution FAILED at stage '{exec_result.error_stage}': {exec_result.error}")

if __name__ == "__main__":
    main()
```

### 8b. Evaluate CO vs AHVG separately

Add to `run_co.py` or create `evaluate_co.py`:

```python
from oll_law_as_code.examples import make_examples
from oll_law_as_code.metric import code_quality_metric

examples = make_examples()
ahvg = [e for e in examples if "ahvg" in e.article_reference.lower()]
co = [e for e in examples if "or " in e.article_reference.lower()]

print(f"AHVG examples: {len(ahvg)}, CO examples: {len(co)}")

for label, subset in [("AHVG", ahvg), ("CO", co)]:
    scores = []
    for ex in subset:
        pred = transformer(
            legal_article_text=ex.legal_article_text,
            article_reference=ex.article_reference,
            available_variables=getattr(ex, "available_variables", ""),
        )
        s = code_quality_metric(ex, pred)
        scores.append(s)
        print(f"  {ex.article_reference}: {s:.2f}")
    if scores:
        print(f"  {label} avg: {sum(scores)/len(scores):.2f}")
```

---

## Execution Order

```
TODO 1 (input variables)     ← prerequisite for all examples
  ↓
TODO 2 (8 YAML examples)     ← highest value, most training signal
  ↓
TODO 3 (metric/runner)       ← needed for accurate scoring
  ↓
TODO 6 (references regex)    ← small, low-risk
  ↓
TODO 5 (personas)            ← extends validation coverage
  ↓
TODO 7 (re-optimize)         ← needs all examples in place first
  ↓
TODO 8 (validate)            ← end-to-end verification
  ↓
TODO 4 (skills)              ← most complex, can be deferred if needed
```

## Summary of Files to Create/Modify

| Action | File |
|---|---|
| **MODIFY** | `src/openfisca_switzerland/variables/inputs.py` |
| **CREATE** | `data/examples/or_art1_contract_formation.yaml` |
| **CREATE** | `data/examples/or_art20_contract_nullity.yaml` |
| **CREATE** | `data/examples/or_art97_contractual_liability.yaml` |
| **CREATE** | `data/examples/or_art62_unjust_enrichment.yaml` |
| **CREATE** | `data/examples/or_art127_prescription.yaml` |
| **CREATE** | `data/examples/or_art55_employer_liability.yaml` |
| **CREATE** | `data/examples/or_art102_debtor_default.yaml` |
| **CREATE** | `data/examples/or_art197_warranty_claims.yaml` |
| **MODIFY** | `src/oll_law_as_code/runner.py` |
| **MODIFY** | `src/oll_law_as_code/metric.py` |
| **CREATE** | `src/oll_law_as_code/skills.py` |
| **CREATE** | `src/oll_law_as_code/skill_transformer.py` |
| **MODIFY** | `src/oll_law_as_code/personas.py` |
| **MODIFY** | `src/oll_law_as_code/persona_runner.py` |
| **MODIFY** | `src/oll_law_as_code/references.py` |
| **MODIFY** | `optimize.py` |
| **CREATE** | `run_co.py` |

## Key Reference Files (read-only, for context)

- `data/legal texts/wiki-CO/pretentions/execution.md` — "keys for judgement" decision tree
- `data/legal texts/wiki-CO/pretentions/dommages-interets.md` — damages claim structures
- `data/legal texts/wiki-CO/pretentions/restitution.md` — restitution claim structures
- `data/examples/or_art41_tort_liability.yaml` — template for all new YAML examples
- `src/bern_stipendium/variables/eligibility.py` — reference for boolean OpenFisca patterns (especially the exclusion pattern `(1 - var)`)
- `src/oll_law_as_code/pipeline.py` — current LegalToCode signature + LegalTransformer
- `data/optimized/legal_transformer.json` — current optimized module (AHVG-only demos)
