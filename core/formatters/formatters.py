# Reference: community\core\formatters\formatters.py
from talon import Module

from ....community.core.formatters.formatters import ImmuneString, format_phrase

mod = Module()


@mod.capture(
    rule="<self.formatters> <user.text_original> (<user.text_original> | <user.formatter_immune>)*"
)
def format_text_codesaway(m) -> str:
    """Formats text and returns a string"""
    out = ""
    formatters = m[0]
    for chunk in m[1:]:
        if isinstance(chunk, ImmuneString):
            out += chunk.string
        else:
            out += format_phrase(chunk, formatters)
    return out
