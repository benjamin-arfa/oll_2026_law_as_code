"""Minimal Swiss OpenFisca country package for AHV/social security modelling."""

import os
from pathlib import Path

from openfisca_core.taxbenefitsystems import TaxBenefitSystem

from openfisca_switzerland.entities import ENTITIES

COUNTRY_DIR = Path(__file__).resolve().parent


class CountryTaxBenefitSystem(TaxBenefitSystem):
    """Swiss tax-benefit system with AHV parameters and base variables."""

    def __init__(self):
        super().__init__(ENTITIES)
        self.add_variables_from_directory(COUNTRY_DIR / "variables")
        param_dir = COUNTRY_DIR / "parameters"
        if param_dir.exists():
            self.load_parameters(str(param_dir))
