from pathlib import Path
from typing import Any, Iterable

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Extra


class BaseModel(PydanticBaseModel):

    # Change default config
    class Config:
        validate_assignment = True
        extra = Extra.allow


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

    def exists(self) -> bool:
        ...  # pragma: no cover

    def read(self) -> Any:
        ...  # pragma: no cover
