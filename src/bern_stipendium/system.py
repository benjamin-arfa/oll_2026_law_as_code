"""Tax-benefit system for the Bern (Switzerland) scholarship rules (ABG).

Bootstrap from openfisca-core. To use:

    from openfisca_core.simulation_builder import SimulationBuilder
    from system import CountryTaxBenefitSystem

    tbs = CountryTaxBenefitSystem()
    sb = SimulationBuilder()
    simulation = sb.build_from_dict(tbs, situation_dict)
    simulation.calculate("stipendium_anspruch", "2024")
"""

import inspect
import os

from openfisca_core.taxbenefitsystems import TaxBenefitSystem
from openfisca_core.variables import Variable

from .entities import entities
from .variables import enums, inputs, eligibility


COUNTRY_DIR = os.path.dirname(os.path.abspath(__file__))


class CountryTaxBenefitSystem(TaxBenefitSystem):
    def __init__(self):
        super().__init__(entities)

        self.load_parameters(os.path.join(COUNTRY_DIR, "parameters"))

        # Register Variable subclasses directly. This avoids
        # `add_variables_from_file`, which calls `get_package_metadata` and
        # logs a malformed warning when the package isn't pip-installed.
        for module in (inputs, eligibility):
            for _, cls in inspect.getmembers(module, inspect.isclass):
                if issubclass(cls, Variable) and cls is not Variable and cls.__module__ == module.__name__:
                    self.add_variable(cls)
