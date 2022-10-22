import pandas as pd

from .class_model import DataBaseModel
from .data import CsvFile
from .decorators import check_existence


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
