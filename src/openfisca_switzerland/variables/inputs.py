"""Stub input variables for the Swiss OpenFisca country package."""

from openfisca_core.model_api import *
from openfisca_switzerland.entities import Person


class gross_monthly_salary(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Gross monthly salary from employment"


class self_employment_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Annual net income from self-employment"


class age(Variable):
    value_type = int
    entity = Person
    definition_period = MONTH
    label = "Age of the person in years"


class has_swiss_residence(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Whether the person has residence in Switzerland"
    default_value = True


class has_swiss_employment(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Whether the person is employed in Switzerland"
    default_value = True


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
