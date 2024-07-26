# https://github.com/AndreasArvidsson/andreas-talon/tree/master/core/on_phrase/analyze_phrase#usage
from talon import settings, speech_system

from .analyze_phrase import analyze_phrase
from .pretty_print_phrase import pretty_print_phrase


def on_post_phrase(phrase):
    if not settings.get("user.pretty_print_phrase"):
        return

    # Get an analyzed phrase
    analyzed_phrase = analyze_phrase(phrase)

    # Pretty print analyzed phrase
    pretty_print_phrase(analyzed_phrase)


speech_system.register("post:phrase", on_post_phrase)
