import pandas as pd

from helpers import PMTHelper
from constants import *


class PMTCalculator:

    def compute_household(self, household_row, member_rows):

        self.missing = False
        self.missing_parts = []
        self.used_parts = []

        # move all calculation logic from compute_pmt()
        # into smaller private methods

        hh_size = self._calculate_household_size(member_rows)

        education = self._calculate_education(member_rows)

        employment = self._calculate_employment(member_rows)

        assets = self._calculate_assets(household_row)

        return self._calculate_score(
            household_row,
            hh_size,
            education,
            employment,
            assets
        )

    def _calculate_household_size(self, members):
        pass

    def _calculate_education(self, members):
        pass

    def _calculate_employment(self, members):
        pass

    def _calculate_assets(self, household):
        pass

    def _calculate_score(
        self,
        household,
        hh_size,
        education,
        employment,
        assets
    ):
        pass