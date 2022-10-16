from collections.abc import Callable
from functools import wraps
from typing import TypeVar

import pandas as pd

from sp.tracker.core.class_model import DataBaseModel

R = TypeVar("R", bound=DataBaseModel)

funcs = {}


def check_existence(func: Callable[[R], pd.DataFrame]) -> Callable[[R], pd.DataFrame]:
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
