import pandas as pd

from sp.tracker.core.class_model import HistoryModel
from sp.tracker.core.decorators import check_existence
from sp.tracker.data.csv import CsvFile


class History(HistoryModel):
    def exists(self) -> bool:
        return self.path.exists() and self.path.is_dir() and len(list(self.path.iterdir())) > 0

    @check_existence
    def read(self, query: str | None) -> pd.DataFrame:

        history_data = []

        for csv_path in self.path.iterdir():
            csv_data = CsvFile(path=csv_path, _columns=self.columns, _actions=self.actions).read(query)
            history_data.append(csv_data)

        return pd.concat(history_data, ignore_index=True)


class TransactionHistory(History):
    _columns = ["Time", "Total (EUR)"]
    _actions = ["Deposit", "Withdraw"]


class DividendHistory(History):
    _columns = [
        "Time",
        "ISIN",
        "Ticker",
        "Name",
        "No. of shares",
        "Price / share",
        "Total (EUR)",
        "Withholding tax",
        "Exchange rate",
    ]
    _actions = ["Dividend (Ordinary)"]


class PositionHistory(History):
    _columns = [
        "Time",
        "ISIN",
        "Ticker",
        "Name",
        "No. of shares",
        "Currency (Price / share)",
        "Price / share",
        "Total (EUR)",
        "Exchange rate",
    ]
    _actions = ["Market buy", "Market sell"]
