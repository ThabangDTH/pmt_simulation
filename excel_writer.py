from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

from constants import *


class ExcelWriter:

    def write(self, results, output_path):

        wb = Workbook()

        self._build_results_sheet(wb, results)
        self._build_summary_sheet(wb, results)

        wb.save(output_path)

    def _build_results_sheet(self, wb, results):
        pass

    def _build_summary_sheet(self, wb, results):
        pass

    def _apply_column_widths(self, ws):
        pass

    def _apply_headers(self, ws):
        pass