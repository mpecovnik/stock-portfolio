import os
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Iterable, TypeVar

import pandas as pd
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Extra, validator


class BaseModel(PydanticBaseModel):

    # Change default config
    class Config:
        validate_assignment = True
        extra = Extra.allow


class ExecutionConfig(BaseModel):
    n_workers: int = 1
    _working: bool = False

    @validator("n_workers")
    @classmethod
    def limit_amount_of_workers(cls, value: int) -> int:
        cpu_count = os.cpu_count()

        if cpu_count is None:
            raise SystemError("Your system has no available cores.")  # pragma: no cover

        n_workers = value if value <= cpu_count else cpu_count // 2
        return n_workers


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
    def wrapper(self: R, query: str | None) -> pd.DataFrame:
        if not self.exists():
            raise ValueError(f"Data for class {self.__class__.__name__} at path: {self.path} doesn't exist.")
        return func(self, query)

    return wrapper


class DataBaseModel(PathModel):
    @check_existence
    def read(self, query: str | None = None) -> pd.DataFrame:  # pylint: disable=unused-argument
        ...  # pragma: no cover


class HistoryModel(DataBaseModel):
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
