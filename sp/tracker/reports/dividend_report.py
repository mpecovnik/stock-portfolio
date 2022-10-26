import pandas as pd

from sp.tracker.data.history import DividendHistory
from sp.tracker.reports.model import ReportBaseModel


class DividendReport(ReportBaseModel):
    history: DividendHistory

    def create_report_in_full(self) -> pd.DataFrame:
        ...  # pragma: no cover

    def create_report_by_ticker(self, ticker: str) -> pd.DataFrame:
        ticker_dividend_history = self.history.read(f"Ticker == '{ticker}'")

        return ticker_dividend_history
