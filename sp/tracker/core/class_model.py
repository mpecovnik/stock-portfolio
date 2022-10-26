import os
from abc import abstractmethod
from pathlib import Path
from typing import Any, Iterable

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


class DataBaseModel(BaseModel):
    path: Path
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

    @abstractmethod
    def exists(self) -> bool:
        ...  # pragma: no cover

    @abstractmethod
    def read(self, query: str | None) -> Any:
        ...  # pragma: no cover
