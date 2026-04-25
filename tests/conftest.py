"""Shared fixtures for the oll_law_as_code test suite."""

import logging

import pytest

from openfisca_switzerland import CountryTaxBenefitSystem


@pytest.fixture(scope="session")
def tax_benefit_system():
    """A shared TaxBenefitSystem instance (expensive to build)."""
    logging.disable(logging.WARNING)
    try:
        return CountryTaxBenefitSystem()
    finally:
        logging.disable(logging.NOTSET)


@pytest.fixture(autouse=True)
def _suppress_openfisca_logging():
    """Suppress openfisca metadata warning during all tests."""
    logging.disable(logging.WARNING)
    yield
    logging.disable(logging.NOTSET)
