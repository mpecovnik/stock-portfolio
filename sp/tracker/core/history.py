import pandas as pd

from sp.tracker.core.class_model import DataBaseModel
from sp.tracker.core.decorators import check_existence


class CsvFile(DataBaseModel):
    def exists(self) -> bool:
        return self.path.exists() and self.path.is_file()

    @check_existence
    def read(self) -> pd.DataFrame:
        data = pd.read_csv(self.path)
        return data.query("Action in @self.actions")[self.columns].copy()


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
