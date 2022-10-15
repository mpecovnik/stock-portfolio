import os
import shutil

import pandas as pd

from sp.tracker.core.class_model import DataBaseModel


class CsvFile(DataBaseModel):
    def exists(self) -> bool:
        return self.path.exists() and self.path.is_file()

    def rm(self) -> None:
        if not self.exists():
            print(f"Skip: {self.path}")
            return

        print(f"Deleting: {self.path}")
        os.remove(self.path)

    def read(self) -> pd.DataFrame:
        if not self.exists():
            raise ValueError(f"CSV partial history at path: {self.path} doesn't exist.")

        data = pd.read_csv(self.path)

        return data.query("Action in @self.actions").copy()[self.columns]

    def write(self, data: pd.DataFrame) -> None:
        root, _ = os.path.split(self.path)
        if not os.path.exists(root):
            os.makedirs(root, exist_ok=True)

        data.to_csv(self.path, index=False)


class History(DataBaseModel):
    def exists(self) -> bool:
        return self.path.exists() and self.path.is_dir() and len(list(self.path.iterdir())) > 0

    def rm(self) -> None:
        if not self.exists():
            print(f"Skip: {self.path}")
            return

        print(f"Deleting: {self.path}")
        shutil.rmtree(self.path, ignore_errors=True)

    def read(self) -> pd.DataFrame:

        if not self.exists():
            raise ValueError(f"History at path: {self.path} doesn't exist.")

        history_data_list = []

        for csv_path in self.path.iterdir():
            csv_item = CsvFile(path=csv_path, _columns=self.columns, _actions=self.actions)
            data = csv_item.read()
            history_data_list.append(data)

        history_data = pd.concat(history_data_list, ignore_index=True)

        return history_data
