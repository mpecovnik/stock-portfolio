from abc import abstractmethod
from concurrent.futures import ProcessPoolExecutor
from typing import List

import pandas as pd

from sp.tracker.core.class_model import BaseModel, ExecutionConfig
from sp.tracker.data.history import History


class ReportBaseModel(BaseModel):
    years: List[int] | None = None
    exec_config: ExecutionConfig = ExecutionConfig()
    history: History

    @abstractmethod
    def create_report_by_ticker(self, ticker: str) -> pd.DataFrame:
        ...  # pragma: no cover

    def create_report(self) -> pd.DataFrame:

        history = self.history.read(None)
        history.loc[:, "YEAR"] = history.Time.astype("datetime64[ns]").apply(lambda x: x.year).values
        history_years = list(history.YEAR.unique())

        if self.years is None:
            self.years = history_years
        else:
            if not set(self.years) <= set(history_years):
                raise ValueError(
                    f"Specified {self.years=} is not contained in history. It only contains {history_years}."
                )

        tickers_in_years = list(history.query(f"YEAR in {self.years}").Ticker.unique())

        with ProcessPoolExecutor(max_workers=self.exec_config.n_workers) as pool:
            results = pool.map(self.create_report_by_ticker, tickers_in_years)

        return pd.concat(results, ignore_index=True)
