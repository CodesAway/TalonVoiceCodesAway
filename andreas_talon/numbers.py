# Reference: https://github.com/AndreasArvidsson/andreas-talon/blob/master/core/numbers/numbers.py
from talon import Context, Module

mod = Module()
ctx = Context()
# ctx.matches = r"""
# tag: user.enable_andreas_talon
# """


@mod.capture(rule="<user.number_string> point <user.number_string>")
def number_float_string(m) -> str:
    """Parses a float number phrase, returning that number as a string."""
    return f"{m.number_string_1}.{m.number_string_2}"


@mod.capture(rule="(numb | number) (<user.number_string> | <user.number_float_string>)")
def number_prefix(m) -> str:
    """Parses a prefixed number phrase, returning that number as a string."""
    try:
        return m.number_string
    except AttributeError:
        return m.number_float_string
