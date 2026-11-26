"""
helpers.py

Utility helper functions for the PMT system.

Responsibilities:
- Safe type conversion
- Date of birth processing
"""

import pandas as pd
import numpy as np
from datetime import date
from constants import MISSING_VALUE, NO_VALUE_SENTINEL, WHERE_LIVING_LABELS


class PMTHelper:
    """
    Utility helper class used across PMT calculations.
    """

    @staticmethod
    def safe_int(value) -> int:
        """
        Safely convert a value to integer.

        Args:
            value: Input value to convert.

        Returns:
            int: Converted integer or MISSING_VALUE if invalid.
        """
        if value is None or (isinstance(value, float) and np.isnan(value)):
            return MISSING_VALUE

        try:
            return int(value)
        except (ValueError, TypeError):
            return MISSING_VALUE

    @staticmethod
    def _is_missing(value) -> bool:
        return (
            value is None
            or (isinstance(value, float) and np.isnan(value))
            or str(value).strip() == NO_VALUE_SENTINEL
        )

    @staticmethod
    def resolve_label(value, label_map: dict) -> int:
        """
        Map a text label to its integer code using the provided lookup.
        Returns MISSING_VALUE if the value is absent or not in the map.
        """
        if PMTHelper._is_missing(value):
            return MISSING_VALUE
        return label_map.get(str(value).strip(), MISSING_VALUE)

    @staticmethod
    def get_living_code(living_elsewhere, where_living) -> int:
        """
        Combine the two living-status columns into a single code:
          1 = in the household
          2 = elsewhere in Lesotho
          3 = in RSA
          4 = in other countries (abroad)
          5 = don't know where
         -1 = missing (only true NaN; 9998 NO VALUE means N/A → in house)

        "9998 NO VALUE" in Living Elsewhere means the question was not asked
        because the member is present in the household (treated as code 1).
        """
        # Genuine null → unknown
        if living_elsewhere is None or (isinstance(living_elsewhere, float) and np.isnan(living_elsewhere)):
            return MISSING_VALUE
        le_str = str(living_elsewhere).strip()
        if le_str in ("No", NO_VALUE_SENTINEL):
            return 1  # present in household
        if le_str == "Yes":
            if PMTHelper._is_missing(where_living):
                return MISSING_VALUE
            return WHERE_LIVING_LABELS.get(str(where_living).strip(), MISSING_VALUE)
        return MISSING_VALUE

    @staticmethod
    def calculate_age(dob) -> int:
        """
        Calculate age from date of birth.

        Args:
            dob: Date of birth (string, datetime, or date).

        Returns:
            int: Age in years or MISSING_VALUE.
        """
        if dob is None or (isinstance(dob, float) and np.isnan(dob)):
            return MISSING_VALUE

        try:
            today = date.today()

            if isinstance(dob, str):
                dob = pd.to_datetime(dob).date()
            elif hasattr(dob, "date"):
                dob = dob.date()

            return int((today - dob).days / 365.25)

        except Exception:
            return MISSING_VALUE