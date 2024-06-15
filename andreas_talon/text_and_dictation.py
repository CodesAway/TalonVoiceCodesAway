# Reference: https://github.com/AndreasArvidsson/andreas-talon/blob/master/core/text/text_and_dictation.py
import re

from talon import Context, Module, actions, grammar

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


# TODO: have tag to allow enabling / disabling this?
@ctx.capture(rule=text_rule)
def text(m) -> str:
    """Mixed words, numbers and punctuation, including user-defined vocabulary, abbreviations and spelling."""
    return format_phrase(m)


# TODO: add text_code and phrase (in original, but omitted in this copy)


# ---------- FORMATTING ---------- #
def format_phrase(m) -> str:
    words = capture_to_words(m)
    result = ""
    for i, word in enumerate(words):
        if i > 0 and needs_space_between(words[i - 1], word):
            if actions.user.dictation_needs_comma_between(words[i - 1], word):
                result += ","
            result += " "
        result += word
    return result


def capture_to_words(m):
    words = []
    for item in m:
        words.extend(
            actions.dictate.parse_words(item)
            if isinstance(item, grammar.vm.Phrase)
            else [item]
        )
    words = actions.dictate.replace_words(words)
    words = actions.user.homophones_replace_words(words)
    return words


# There must be a simpler way to do this, but I don't see it right now.
no_space_after = re.compile(
    r"""
  (?:
    [\s\-_/#@([{‘“]     # characters that never need space after them
  | (?<!\w)[$£€¥₩₽₹]    # currency symbols not preceded by a word character
  # quotes preceded by beginning of string, space, opening braces, dash, or other quotes
  | (?: ^ | [\s([{\-'"] ) ['"]
  )$""",
    re.VERBOSE,
)
no_space_before = re.compile(
    r"""
  ^(?:
    [\s\-_.,!?;:/%)\]}’”]   # characters that never need space before them
  | [$£€¥₩₽₹](?!\w)         # currency symbols not followed by a word character
  # quotes followed by end of string, space, closing braces, dash, other quotes, or some punctuation.
  | ['"] (?: $ | [\s)\]}\-'".,!?;:/] )
  )""",
    re.VERBOSE,
)


def omit_space_before(text: str) -> bool:
    return not text or no_space_before.search(text) is not None


def omit_space_after(text: str) -> bool:
    return not text or no_space_after.search(text) is not None


def needs_space_between(before: str, after: str) -> bool:
    return not (omit_space_after(before) or omit_space_before(after))


@mod.action_class
class Actions:
    def dictation_needs_comma_between(before: str, after: str) -> bool:
        """Returns true if a `,` should be inserted between these words during dictation"""
        return after == "but" and before[-1].isalpha()
