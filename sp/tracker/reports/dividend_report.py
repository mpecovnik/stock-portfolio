import pandas as pd

from sp.tracker.core.class_model import ReportBaseModel
from sp.tracker.data.history import DividendHistory


class DividendReport(ReportBaseModel):
    dividend_history: DividendHistory

    def create_report_in_full(self) -> pd.DataFrame:
        ...  # pragma: no cover

    def create_report_by_ticker(self, ticker: str) -> pd.DataFrame:
        ticker_dividend_history = self.dividend_history.read(f"Ticker == '{ticker}'")

        return ticker_dividend_history
