# Reference: https://github.com/AndreasArvidsson/andreas-talon/blob/master/core/abbreviation/abbreviation.py
from talon import Module

mod = Module()


@mod.capture(rule="brief {user.abbreviation}")
def abbreviation(m) -> str:
    """Abbreviated words"""
    return m.abbreviation
