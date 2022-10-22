import pandas as pd

from sp.tracker.core.class_model import DataBaseModel
from sp.tracker.core.decorators import check_existence
from sp.tracker.data.csv import CsvFile


class History(DataBaseModel):
    def exists(self) -> bool:
        return self.path.exists() and self.path.is_dir() and len(list(self.path.iterdir())) > 0

    @check_existence
    def read(self) -> pd.DataFrame:

        history_data = []

        for csv_path in self.path.iterdir():
            csv_item = CsvFile(path=csv_path, _columns=self.columns, _actions=self.actions)
            history_data.append(csv_item.read())

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
        "Price / Share",
        "Total (EUR)",
        "Witholding tax",
    ]
    _actions = ["Dividend (Ordinary)"]


class PositionHistory(History):
    _columns = [
        "Time",
        "ISIN",
        "Ticker",
        "Name",
        "No. of shares",
        "Currency (Price / Share)",
        "Price / Share",
        "Total (EUR)",
    ]
    _actions = ["Market buy", "Market sell"]
