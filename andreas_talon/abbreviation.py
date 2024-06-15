# Reference: https://github.com/AndreasArvidsson/andreas-talon/blob/master/core/abbreviation/abbreviation.py
from talon import Context, Module

mod = Module()
ctx = Context()
# ctx.matches = r"""
# tag: user.enable_andreas_talon
# """


@mod.capture(rule="brief {user.abbreviation}")
def abbreviation(m) -> str:
    """Abbreviated words"""
    return m.abbreviation
