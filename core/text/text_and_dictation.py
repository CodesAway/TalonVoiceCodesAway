# Reference: https://github.com/AndreasArvidsson/andreas-talon/blob/master/core/text/text_and_dictation.py

from talon import Module

from ....community.core.text.text_and_dictation import format_phrase

mod = Module()


# Tweaked from original
@mod.capture(rule="spell {user.letter}+")
def spell(m) -> str:
    """Spell word phoneticly"""
    return "".join(m.letter_list)


text_rule_parts = [
    "{user.vocabulary}",
    "{user.key_punctuation_codesaway}",
    "<user.abbreviation>",
    "<user.spell>",
    "<user.number_prefix>",
    "<phrase>",
]

text_rule = f"({'|'.join(text_rule_parts)})+"


@mod.capture(rule=text_rule)
def text_codesaway(m) -> str:
    """Mixed words, numbers and punctuation, including user-defined vocabulary, abbreviations and spelling."""
    # TODO: how to handle writing code such as "code action dot mimic" which want to result in action.mimic
    # Currently, adds space after '.' which is logical for text, but not code (how to override?)
    return format_phrase(m)
