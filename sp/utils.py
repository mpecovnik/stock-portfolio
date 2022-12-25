from typing import TypeVar

from .model import BaseModel

PRECISION_GUARD = 1e-9

A = TypeVar("A", bound="Action")


class Action(BaseModel):
    type: str
    date: str
    num_shares: float
    price: float

    def __sub__(self: A, other: A) -> A:
        returned_action = self.copy()
        returned_action.num_shares -= other.num_shares

        return returned_action


class BuyAction(Action):
    type = "Buy"


class SellAction(Action):
    type = "Sell"
