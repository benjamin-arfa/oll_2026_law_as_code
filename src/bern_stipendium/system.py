"""Tax-benefit system for the Bern (Switzerland) scholarship rules (ABG).

Bootstrap from openfisca-core. To use:

    from openfisca_core.simulation_builder import SimulationBuilder
    from system import CountryTaxBenefitSystem

    tbs = CountryTaxBenefitSystem()
    sb = SimulationBuilder()
    simulation = sb.build_from_dict(tbs, situation_dict)
    simulation.calculate("stipendium_anspruch", "2024")
"""

import os

from openfisca_core.taxbenefitsystems import TaxBenefitSystem

from .entities import entities
from .variables import enums, inputs, eligibility


COUNTRY_DIR = os.path.dirname(os.path.abspath(__file__))


class CountryTaxBenefitSystem(TaxBenefitSystem):
    def __init__(self):
        super().__init__(entities)

        # Load all parameter YAML files (recursively walks the directory)
        self.load_parameters(os.path.join(COUNTRY_DIR, "parameters"))

        # Register every Variable defined in our modules.
        for module in (inputs, eligibility):
            self.add_variables_from_file(module.__file__)
