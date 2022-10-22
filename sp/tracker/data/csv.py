import pandas as pd

from sp.tracker.core.class_model import DataBaseModel
from sp.tracker.core.decorators import check_existence


class CsvFile(DataBaseModel):
    def exists(self) -> bool:
        return self.path.exists() and self.path.is_file()

    @check_existence
    def read(self, query: str | None) -> pd.DataFrame:
        data = pd.read_csv(self.path)

        if query is not None:
            data = data.query(query).copy()

        return data.query("Action in @self.actions")[self.columns].copy()
