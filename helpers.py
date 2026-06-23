import pandas as pd
import numpy as np
from datetime import date

from constants import MISSING_VALUE


class PMTHelper:

    @staticmethod
    def safe_int(value):
        if value is None or (isinstance(value, float) and np.isnan(value)):
            return MISSING_VALUE

        try:
            return int(value)
        except (TypeError, ValueError):
            return MISSING_VALUE

    @staticmethod
    def calculate_age(dob):
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