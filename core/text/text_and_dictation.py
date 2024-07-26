# Reference: https://github.com/AndreasArvidsson/andreas-talon/blob/master/core/text/text_and_dictation.py

import re

from talon import Module

from ....community.core.text.text_and_dictation import capture_to_words, format_phrase

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
code_rule = text_rule.replace(
    "{user.key_punctuation_codesaway}", "{user.key_punctuation_code_codesaway}"
)


@mod.capture(rule=text_rule)
def text_codesaway(m) -> str:
    """Mixed words, numbers and punctuation, including user-defined vocabulary, abbreviations and spelling."""
    return format_phrase(m)


@mod.capture(rule=code_rule)
def text_code_codesaway(m) -> str:
    """Mixed words, numbers and punctuation, including user-defined vocabulary, abbreviations and spelling."""
    return format_code_phrase(m)


# ---------- FORMATTING ---------- #
def format_code_phrase(m) -> str:
    # Reference: community\core\text\text_and_dictation.py -> format_phrase
    # (same as format_code in community, but doesn't add space after ".")
    words = capture_to_words(m)
    result = ""
    for i, word in enumerate(words):
        if i > 0 and needs_space_between(words[i - 1], word):
            result += " "
        result += word
    return result


# There must be a simpler way to do this, but I don't see it right now.
no_space_after = re.compile(
    r"""
  (?:
    [.\s\-_/#@([{‘“]     # characters that never need space after them (added dot for code)
  | (?<!\w)[$£€¥₩₽₹]    # currency symbols not preceded by a word character
  # quotes preceded by beginning of string, space, opening braces, dash, or other quotes
  | (?: ^ | [\s([{\-'"] ) ['"]
  )$""",
    re.VERBOSE,
)
no_space_before = re.compile(
    r"""
  ^(?:
    [\s\-_.,!?/%)\]}’”]   # characters that never need space before them
  | [$£€¥₩₽₹](?!\w)        # currency symbols not followed by a word character
  | [;:](?!-\)|-\()        # colon or semicolon except for smiley faces
  # quotes followed by end of string, space, closing braces, dash, other quotes, or some punctuation.
  | ['"] (?: $ | [\s)\]}\-'".,!?;:/] )
  # apostrophe s
  | 's(?!\w)
  )""",
    re.VERBOSE,
)


def omit_space_before(text: str) -> bool:
    return not text or no_space_before.search(text)


def omit_space_after(text: str) -> bool:
    return not text or no_space_after.search(text)


def needs_space_between(before: str, after: str) -> bool:
    return not (omit_space_after(before) or omit_space_before(after))
