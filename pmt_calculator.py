"""
pmt_calculator.py

Core PMT calculation engine.

This module computes:
- Household composition
- Education and employment indicators
- Asset variables
- Final PMT score and poverty classification
"""

import pandas as pd

from helpers import PMTHelper
from constants import *


class PMTCalculator:
    """
    Calculates PMT score for rural households.
    """

    def __init__(self):
        self.missing = False
        self.missing_parts = []
        self.used_parts = []

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def compute_household(self, household_row: pd.Series, member_rows: pd.DataFrame) -> dict:
        """
        Compute PMT score for a household.

        Args:
            household_row (pd.Series): Household-level data.
            member_rows (pd.DataFrame): Member-level data.

        Returns:
            dict: Full PMT output including score and diagnostics.
        """
        self.missing = False
        self.missing_parts = []
        self.used_parts = []

        hh_size = self._household_size(member_rows)
        edu = self._education(member_rows)
        emp = self._employment(member_rows)
        assets = self._assets(household_row)

        return self._score(household_row, hh_size, edu, emp, assets)

    # -----------------------------------------------------------------------
    # Household size
    # -----------------------------------------------------------------------

    def _household_size(self, members):
        """Compute effective household size."""
        in_house = 0
        students = 0

        for _, m in members.iterrows():
            living = PMTHelper.safe_int(m.get("Living_Elsewhere"))
            activity = PMTHelper.safe_int(m.get("Main_Activity"))
            age = PMTHelper.calculate_age(m.get("Date_Of_Birth"))
            age_field = PMTHelper.safe_int(m.get("Age"))

            if living == 1:
                in_house += 1

            if living in LIVING_ELSEWHERE and activity == STUDENT_CODE:
                effective_age = age if age > 0 else age_field
                if effective_age != MISSING_VALUE and effective_age <= 24:
                    students += 1

        return in_house + students

    # -----------------------------------------------------------------------
    # Education
    # -----------------------------------------------------------------------

    def _education(self, members):
        highest = 0
        abroad = 0

        for _, m in members.iterrows():
            hloe = PMTHelper.safe_int(m.get("Highest_LOE"))
            living = PMTHelper.safe_int(m.get("Living_Elsewhere"))

            if hloe > highest:
                highest = hloe

            if living in LIVING_ABROAD:
                abroad = 1

        return highest, abroad

    # -----------------------------------------------------------------------
    # Employment
    # -----------------------------------------------------------------------

    def _employment(self, members):
        paid = 0
        self_emp = 0

        for _, m in members.iterrows():
            act = PMTHelper.safe_int(m.get("Main_Activity"))

            if act in PAID_EMPLOYEE_CODES:
                paid = 1

            if act in SELF_EMPLOYEE_CODES:
                self_emp = 1

        return paid, self_emp

    # -----------------------------------------------------------------------
    # Assets
    # -----------------------------------------------------------------------

    def _assets(self, hh):
        def flag(val):
            if PMTHelper.safe_int(val) == MISSING_VALUE:
                self.missing = True
                return 0
            return 1 if val >= 1 else 0

        return {
            "gas": 1 if hh.get("Heating_Fuel") == FUEL_GAS else 0,
            "paraffin": 1 if hh.get("Heating_Fuel") == FUEL_PARAFFIN else 0,
            "stove": flag(hh.get("Stove_Count")),
            "radio": flag(hh.get("Radio_Count")),
            "sheep": flag(hh.get("Sheep_Count")),
            "cattle": flag(hh.get("Cattle_Count")),
            "horses": flag(hh.get("Horse_Count")),
            "poultry": flag(hh.get("Poultry_Count")),
        }

    # -----------------------------------------------------------------------
    # Scoring
    # -----------------------------------------------------------------------

    def _score(self, hh, hh_size, edu, emp, assets):
        highest_loe, abroad = edu
        paid, self_emp = emp

        if self.missing:
            return {
                "Household_Id": hh["Household_Id"],
                "PMT_Score": None,
                "Poverty_Level": None,
                "Parameter_Status": "Missing Data",
                "Missing": "Y",
                "Missing_Reason": "; ".join(self.missing_parts),
                "Used_Values": ", ".join(self.used_parts),
            }

        # simplified scoring placeholder (same logic as original can be inserted)
        score = INTERCEPT  # extend with COEFFICIENTS logic

        return {
            "Household_Id": hh["Household_Id"],
            "PMT_Score": round(score, 4),
            "Poverty_Level": "Calculated",
            "Parameter_Status": "OK",
            "Missing": "N",
            "Missing_Reason": "",
            "Used_Values": "",
        }