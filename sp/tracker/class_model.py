from pathlib import Path

from pydantic import Extra
from pydantic.generics import GenericModel


class BaseGenericModel(GenericModel):

    # Change default config
    class Config:
        validate_assignment = True
        extra = Extra.forbid


class DataBaseGenericModel(BaseGenericModel):
    path: Path
