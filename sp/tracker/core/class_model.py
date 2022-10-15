from pathlib import Path
from typing import List

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Extra


class BaseModel(PydanticBaseModel):

    # Change default config
    class Config:
        validate_assignment = True
        extra = Extra.allow


class DataBaseModel(BaseModel):
    path: Path
    _columns: List[str] | None = None
    _actions: List[str] | None = None

    @property
    def columns(self) -> List[str]:
        if self._columns is None:
            raise ValueError("Property '_columns' must be set by concrete class implementations.")

        return list(set(self._columns) | {"Action"})

    @property
    def actions(self) -> List[str]:
        if self._actions is None:
            raise ValueError("Property '_actions' must be set by concrete class implementations.")

        return self._actions
