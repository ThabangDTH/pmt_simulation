"""
main.py

Entry point for PMT application.

Usage:
    python main.py input.xlsx output.xlsx
"""

import sys
import pandas as pd

from pmt_calculator import PMTCalculator
from excel_writer import ExcelWriter
from constants import INPUT_SHEET_HOUSEHOLDS, INPUT_SHEET_MEMBERS


class PMTApplication:
    """
    Orchestrates PMT workflow:
    - Load data
    - Run calculations
    - Generate output
    """

    def __init__(self):
        self.calculator = PMTCalculator()
        self.writer = ExcelWriter()

    def run(self, input_path: str, output_path: str) -> None:
        """
        Execute full PMT pipeline.

        Args:
            input_path: Input Excel file path.
            output_path: Output Excel file path.
        """
        xls = pd.ExcelFile(input_path)

        households = pd.read_excel(xls, sheet_name=INPUT_SHEET_HOUSEHOLDS)
        members = pd.read_excel(xls, sheet_name=INPUT_SHEET_MEMBERS)

        households.columns = [c.strip().replace(" ", "_") for c in households.columns]
        members.columns = [c.strip().replace(" ", "_") for c in members.columns]

        results = []

        for _, hh in households.iterrows():
            hh_members = members[members["Household_Id"] == hh["Household_Id"]]
            results.append(self.calculator.compute_household(hh, hh_members))

        self.writer.write(results, output_path)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py input.xlsx output.xlsx")
        sys.exit(1)

    PMTApplication().run(sys.argv[1], sys.argv[2])