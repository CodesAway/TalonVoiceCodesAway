# Reference: https://github.com/AndreasArvidsson/andreas-talon/blob/master/core/text/text_and_dictation.py

from talon import Context, Module

from ...community.core.text.text_and_dictation import format_phrase

mod = Module()

ctx = Context()
ctx.matches = r"""
tag: user.enable_andreas_talon
"""


@ctx.capture("user.text", rule="<user.text_codesaway>")
def text(m) -> str:
    """Mixed words, numbers and punctuation, including user-defined vocabulary, abbreviations and spelling."""
    return format_phrase(m)


# TODO: add text_code and phrase (in original, but omitted in this copy)
