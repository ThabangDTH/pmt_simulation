"""
main.py

Entry point for PMT application.

Usage:
    python main.py                          # batch: processes all Input/*.xlsx files
    python main.py input.xlsx output.xlsx   # single file
"""

import os
import sys
import glob
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
        Execute full PMT pipeline for a single file.

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
            hh_members = members[members["HouseholdId"] == hh["HouseholdId"]]
            results.append(self.calculator.compute_household(hh, hh_members))

        self.writer.write(results, output_path)

    def run_batch(self, input_dir: str = "Input", output_dir: str = "Output") -> None:
        """
        Process all .xlsx files in input_dir that are not prefixed with 'Output_'.

        Args:
            input_dir: Folder containing input workbooks.
            output_dir: Folder where output workbooks will be written.
        """
        os.makedirs(output_dir, exist_ok=True)

        pattern = os.path.join(input_dir, "*.xlsx")
        input_files = [
            f for f in glob.glob(pattern)
            if not os.path.basename(f).startswith("Output_")
        ]

        if not input_files:
            print(f"No input files found in '{input_dir}'.")
            return

        for input_path in sorted(input_files):
            name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(output_dir, f"Output_{name}.xlsx")
            print(f"Processing {input_path} -> {output_path}")
            self.run(input_path, output_path)

        print(f"\nDone. {len(input_files)} file(s) written to '{output_dir}'.")


if __name__ == "__main__":
    app = PMTApplication()

    if len(sys.argv) == 1:
        app.run_batch()
    elif len(sys.argv) == 3:
        app.run(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python main.py                          # batch mode")
        print("       python main.py input.xlsx output.xlsx   # single file")
        sys.exit(1)