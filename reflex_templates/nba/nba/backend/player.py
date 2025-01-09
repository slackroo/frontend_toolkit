import reflex as rx
from typing import Union


class Player(rx.Base):
    """The player class."""

    name: str
    team: str
    number: int
    position: str
    age: int
    height: str
    weight: int
    college: str
    salary: Union[int, str]  # Can also be a string for the NaN values
