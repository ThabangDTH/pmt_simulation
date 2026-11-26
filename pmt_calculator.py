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

        # Household size: count members with HouseholdMember_Status == 1.
        # Status 0 means the member has been removed from the roster.
        if COL_MEMBER_STATUS in member_rows.columns:
            active_members = member_rows[member_rows[COL_MEMBER_STATUS] == 1]
        else:
            active_members = member_rows

        hh_size = len(active_members)
        self.used_parts.append(f"HHSize:{hh_size}")

        edu, edu_missing = self._education(active_members)
        emp, emp_missing = self._employment(active_members)
        assets, assets_missing = self._assets(household_row)

        # All gaps are noted but never block scoring — defaults (0) are used for any
        # missing variable so a score is always produced.
        noted_reasons = edu_missing + emp_missing + list(assets_missing)

        if hh_size == 0:
            hh_id = household_row.get("HouseholdId", "unknown")
            noted_reasons.append(f"HH Size of 0 for household id:{hh_id}")

        self.missing_parts = noted_reasons
        self.missing = False

        return self._score(household_row, hh_size, edu, emp, assets)

    # -----------------------------------------------------------------------
    # Education
    # -----------------------------------------------------------------------

    def _education(self, members):
        highest = 0
        abroad = 0
        missing_reasons = []

        hloe_col = COL_HIGHEST_LOE.replace(" ", "_")
        living_col = COL_WHERE_MEMBER_LIVING.replace(" ", "_")
        living_elsewhere_col = COL_LIVING_ELSEWHERE.replace(" ", "_")

        for _, m in members.iterrows():
            member_id = m.get(COL_MEMBER_ID, "unknown")
            hloe = PMTHelper.resolve_label(m.get(hloe_col), HIGHEST_LOE_LABELS)
            living = PMTHelper.get_living_code(m.get(living_elsewhere_col), m.get(living_col))

            if hloe == MISSING_VALUE:
                missing_reasons.append(f"HighestLOE for member id:{member_id}")
            elif hloe > highest:
                highest = hloe

            if living in LIVING_ABROAD:
                abroad = 1

        self.used_parts.append(f"HighestLOE:{highest}")
        self.used_parts.append(f"MemberAbroad:{abroad}")
        return (highest, abroad), missing_reasons

    # -----------------------------------------------------------------------
    # Employment
    # -----------------------------------------------------------------------

    def _employment(self, members):
        paid = 0
        self_emp = 0
        missing_reasons = []

        activity_col = COL_MAIN_ACTIVITY.replace(" ", "_")

        for _, m in members.iterrows():
            member_id = m.get(COL_MEMBER_ID, "unknown")
            act = PMTHelper.resolve_label(m.get(activity_col), MAIN_ACTIVITY_LABELS)

            if act == MISSING_VALUE:
                missing_reasons.append(f"MainActivity for member id:{member_id}")
            else:
                if act in PAID_EMPLOYEE_CODES:
                    paid = 1
                if act in SELF_EMPLOYEE_CODES:
                    self_emp = 1

        self.used_parts.append(f"PaidEmployee:{paid}")
        self.used_parts.append(f"SelfEmployee:{self_emp}")
        return (paid, self_emp), missing_reasons

    # -----------------------------------------------------------------------
    # Assets
    # -----------------------------------------------------------------------

    def _assets(self, hh):
        def flag(val, name):
            if PMTHelper.safe_int(val) == MISSING_VALUE:
                return 0, f"{name} for household id:{hh.get('HouseholdId')}"
            return 1 if PMTHelper.safe_int(val) >= 1 else 0, None

        missing_reasons = []
        hh_id = hh.get("HouseholdId")

        # Heating fuel from household (not members)
        heating_col = COL_HEATING_FUEL.replace(" ", "_")
        heating_fuel = PMTHelper.resolve_label(hh.get(heating_col), HEATING_FUEL_LABELS)

        if heating_fuel == MISSING_VALUE:
            missing_reasons.append(f"HeatingFuel defaulted to 0 for household id:{hh_id}")
            gas = 0
            paraffin = 0
        else:
            gas = 1 if heating_fuel == FUEL_GAS else 0
            paraffin = 1 if heating_fuel == FUEL_PARAFFIN else 0
            self.used_parts.append(f"Heating Fuel:{heating_fuel}")

        # Asset counts
        stove, stove_missing = flag(hh.get(COL_STOVES.replace(" ", "_")), "# Stoves")
        radio, radio_missing = flag(hh.get(COL_RADIOS.replace(" ", "_")), "# Radios")
        sheep, sheep_missing = flag(hh.get(COL_SHEEP.replace(" ", "_")), "# Sheep")
        cattle, cattle_missing = flag(hh.get(COL_CATTLE.replace(" ", "_")), "# Cattle")
        horses, horses_missing = flag(hh.get(COL_HORSES.replace(" ", "_")), "# Horses")
        poultry, poultry_missing = flag(hh.get(COL_POULTRY.replace(" ", "_")), "# Poultry")

        for miss in [stove_missing, radio_missing, sheep_missing, cattle_missing, horses_missing, poultry_missing]:
            if miss:
                missing_reasons.append(miss)

        if stove_missing is None:
            self.used_parts.append(f"# Stoves:{PMTHelper.safe_int(hh.get(COL_STOVES.replace(' ', '_')))}")
        if radio_missing is None:
            self.used_parts.append(f"# Radios:{PMTHelper.safe_int(hh.get(COL_RADIOS.replace(' ', '_')))}")
        if sheep_missing is None:
            self.used_parts.append(f"# Sheep:{PMTHelper.safe_int(hh.get(COL_SHEEP.replace(' ', '_')))}")
        if cattle_missing is None:
            self.used_parts.append(f"# Cattle:{PMTHelper.safe_int(hh.get(COL_CATTLE.replace(' ', '_')))}")
        if horses_missing is None:
            self.used_parts.append(f"# Horses:{PMTHelper.safe_int(hh.get(COL_HORSES.replace(' ', '_')))}")
        if poultry_missing is None:
            self.used_parts.append(f"# Poultry:{PMTHelper.safe_int(hh.get(COL_POULTRY.replace(' ', '_')))}")

        return {
            "heating_fuel": heating_fuel if heating_fuel != MISSING_VALUE else None,
            "gas": gas,
            "paraffin": paraffin,
            "stove": stove,
            "radio": radio,
            "sheep": sheep,
            "cattle": cattle,
            "horses": horses,
            "poultry": poultry,
        }, missing_reasons

    # -----------------------------------------------------------------------
    # Scoring
    # -----------------------------------------------------------------------

    def _score(self, hh, hh_size, edu, emp, assets):
        highest_loe, abroad = edu
        paid, self_emp = emp

        # Size 1 uses size-2 coefficient (no size-1 dummy in the model).
        # Size 7+ all use the size-7 coefficient.
        effective_size = max(hh_size, 2)

        var_size2 = 1 if effective_size == 2 else 0
        var_size3 = 1 if effective_size == 3 else 0
        var_size4 = 1 if effective_size == 4 else 0
        var_size5 = 1 if effective_size == 5 else 0
        var_size6 = 1 if effective_size == 6 else 0
        var_size7 = 1 if effective_size > 6 else 0

        # Generate education dummy variables
        var_eduprimary = 1 if highest_loe in (3, 4, 5) else 0
        var_edusecondary = 1 if highest_loe in (6, 7, 8) else 0
        var_eduoversecondary = 1 if highest_loe > 8 else 0

        # Generate other dummy variables
        var_memberabroad = abroad
        var_paidemp = paid
        var_selfemp = self_emp

        base = {
            "Household_Id": hh["HouseholdId"],
            "HH_Size": hh_size,
            "Effective_Size": effective_size,
            "Highest_LOE": highest_loe,
            "Member_Abroad": abroad,
            "Paid_Employee": paid,
            "Self_Employee": self_emp,
            "Heating_Fuel_Code": assets["heating_fuel"],
            "var_gas": assets["gas"],
            "var_paraffin": assets["paraffin"],
            "var_stove": assets["stove"],
            "var_radio": assets["radio"],
            "var_sheep": assets["sheep"],
            "var_cattle": assets["cattle"],
            "var_horses": assets["horses"],
            "var_poultry": assets["poultry"],
            "var_size2": var_size2,
            "var_size3": var_size3,
            "var_size4": var_size4,
            "var_size5": var_size5,
            "var_size6": var_size6,
            "var_size7": var_size7,
            "var_eduprimary": var_eduprimary,
            "var_edusecondary": var_edusecondary,
            "var_eduoversecondary": var_eduoversecondary,
        }

        # Household with no active members gets a forced score of 0.
        if hh_size == 0:
            return {
                **base,
                "PMT_Score": 0,
                "Poverty_Level": "Poor",
                "Parameter_Status": "Partial Data",
                "Missing": "Y",
                "Missing_Reason": "; ".join(self.missing_parts),
                "Used_Values": ", ".join(self.used_parts),
            }

        # Full PMT calculation
        var_calc = (
            INTERCEPT +
            var_size2 * COEFFICIENTS["size2"] +
            var_size3 * COEFFICIENTS["size3"] +
            var_size4 * COEFFICIENTS["size4"] +
            var_size5 * COEFFICIENTS["size5"] +
            var_size6 * COEFFICIENTS["size6"] +
            var_size7 * COEFFICIENTS["size7"] +
            var_eduprimary * COEFFICIENTS["eduprimary"] +
            var_edusecondary * COEFFICIENTS["edusecondary"] +
            var_eduoversecondary * COEFFICIENTS["eduoversecondary"] +
            var_memberabroad * COEFFICIENTS["memberabroad"] +
            var_paidemp * COEFFICIENTS["paidemp"] +
            var_selfemp * COEFFICIENTS["selfemp"] +
            assets["gas"] * COEFFICIENTS["gas"] +
            assets["paraffin"] * COEFFICIENTS["paraffin"] +
            assets["stove"] * COEFFICIENTS["stove"] +
            assets["radio"] * COEFFICIENTS["radio"] +
            assets["sheep"] * COEFFICIENTS["sheep"] +
            assets["cattle"] * COEFFICIENTS["cattle"] +
            assets["horses"] * COEFFICIENTS["horses"] +
            assets["poultry"] * COEFFICIENTS["poultry"]
        )

        var_totalcalc = (var_calc - POVERTY_MEAN) * POVERTY_SCALE

        poverty_level = "Poor" if var_totalcalc < POVERTY_CUTOFF else "Better-Off"

        status = "Partial Data" if self.missing_parts else "OK"

        return {
            **base,
            "PMT_Score": round(var_totalcalc, 4),
            "Poverty_Level": poverty_level,
            "Parameter_Status": status,
            "Missing": "Y" if self.missing_parts else "N",
            "Missing_Reason": "; ".join(self.missing_parts),
            "Used_Values": ", ".join(self.used_parts),
        }