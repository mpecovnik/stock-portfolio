from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Iterable, TypeVar, List, Optional
from abc import abstractmethod
from concurrent.futures import ProcessPoolExecutor
import os

import pandas as pd
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Extra, validator


class BaseModel(PydanticBaseModel):

    # Change default config
    class Config:
        validate_assignment = True
        extra = Extra.allow


class PathModel(BaseModel):
    path: Path

    def exists(self) -> bool:
        ...  # pragma: no cover


R = TypeVar("R", bound=PathModel)

funcs = {}


def check_existence(func: Callable[[R, str | None], pd.DataFrame]) -> Callable[[R, str | None], pd.DataFrame]:
    """Register any function at definition time in
    the 'funcs' dict."""

    # Registers the function during function definition time.
    funcs[func.__name__] = func

    @wraps(func)
    def wrapper(self: R) -> pd.DataFrame:
        if not self.exists():
            raise ValueError(f"Data for class {self.__class__.__name__} at path: {self.path} doesn't exist.")
        return func(self)

    return wrapper


class HistoryModel(PathModel):
    query: str | None = None
    _columns: Iterable[str] | None = None
    _actions: Iterable[str] | None = None

    @property
    def columns(self) -> Iterable[str]:
        if self._columns is None:
            raise AttributeError("Property '_columns' must be set by concrete class implementations.")

        return list(set(self._columns) | {"Action"})

    @property
    def actions(self) -> Iterable[str]:
        if self._actions is None:
            raise AttributeError("Property '_actions' must be set by concrete class implementations.")

        return self._actions

    @property
    def read_query(self) -> str:
        return f"Action in {list(self.actions)}" if self.query is None else f"Action in {list(self.actions)} and {self.query}"

    def exists(self) -> bool:
        return self.path.exists() and self.path.is_dir() and len(list(self.path.iterdir())) > 0

    @check_existence
    def read(self) -> pd.DataFrame:
        return pd.concat(
            [pd.read_csv(csv_path, usecols=list(self.columns)).query(self.read_query) for csv_path in self.path.iterdir()],
            ignore_index=True,
        )


class ReportModel(BaseModel):
    years: List[int] | None = None
    history: HistoryModel
    n_workers: Optional[int] = None

    @validator("n_workers")
    @classmethod
    def limit_amount_of_workers(cls, value: int) -> int:
        cpu_count = os.cpu_count()

        if cpu_count is None:
            raise SystemError("Your system has no available cores.")  # pragma: no cover

        return value if value <= cpu_count else cpu_count

    @abstractmethod
    def create_report_by_ticker(self, ticker: str) -> pd.DataFrame:
        ...  # pragma: no cover

    def create_report(self) -> pd.DataFrame:

        history = self.history.read()
        history.loc[:, "YEAR"] = history.Time.astype("datetime64[ns]").apply(lambda x: x.year).values
        history_years = list(history.YEAR.unique())

        if self.years is not None and not set(self.years) <= set(history_years):
            raise ValueError(f"Specified {self.years=} is not contained in history. It only contains {history_years}.")

        tickers_in_years = list(history.query(f"YEAR in {history_years}").Ticker.unique())

        with ProcessPoolExecutor(max_workers=self.exec_config.n_workers) as pool:
            results = pool.map(self.create_report_by_ticker, tickers_in_years)

        return pd.concat(results, ignore_index=True)
