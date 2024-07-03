# Reference: https://github.com/AndreasArvidsson/andreas-talon/blob/master/core/text/text_and_dictation.py

from talon import Context, Module

from ...community.core.text.text_and_dictation import format_phrase

mod = Module()

ctx = Context()
ctx.matches = r"""
tag: user.enable_andreas_talon
"""

# ----- Captures used in both command and dictation mode -----


# Tweaked from original
@mod.capture(rule="spell {user.letter}+")
def spell(m) -> str:
    """Spell word phoneticly"""
    return "".join(m.letter_list)


text_rule_parts = [
    "{user.vocabulary}",
    # "{user.key_punctuation}", # Commented out (for now at least)
    "<user.abbreviation>",
    "<user.spell>",
    "<user.number_prefix>",
    "<phrase>",
]

text_rule = f"({'|'.join(text_rule_parts)})+"


@ctx.capture("user.text", rule=text_rule)
def text(m) -> str:
    """Mixed words, numbers and punctuation, including user-defined vocabulary, abbreviations and spelling."""
    return format_phrase(m)


# TODO: add text_code and phrase (in original, but omitted in this copy)
