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
