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
from constants import MISSING_VALUE


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