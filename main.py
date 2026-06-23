import pandas as pd
import sys

from constants import (
    INPUT_SHEET_HOUSEHOLDS,
    INPUT_SHEET_MEMBERS,
)

from pmt_calculator import PMTCalculator
from excel_writer import ExcelWriter


class PMTApplication:

    def __init__(self):
        self.calculator = PMTCalculator()
        self.writer = ExcelWriter()

    def run(self, input_path, output_path):

        xls = pd.ExcelFile(input_path)

        households = pd.read_excel(
            xls,
            sheet_name=INPUT_SHEET_HOUSEHOLDS
        )

        members = pd.read_excel(
            xls,
            sheet_name=INPUT_SHEET_MEMBERS
        )

        households.columns = [
            c.strip().replace(" ", "_")
            for c in households.columns
        ]

        members.columns = [
            c.strip().replace(" ", "_")
            for c in members.columns
        ]

        results = []

        for _, household in households.iterrows():

            household_members = members[
                members["Household_Id"]
                == household["Household_Id"]
            ]

            results.append(
                self.calculator.compute_household(
                    household,
                    household_members
                )
            )

        self.writer.write(results, output_path)


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print(
            "Usage: python main.py input.xlsx output.xlsx"
        )
        sys.exit(1)

    PMTApplication().run(
        sys.argv[1],
        sys.argv[2]
    )