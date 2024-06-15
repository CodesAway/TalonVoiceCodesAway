# Reference: https://github.com/AndreasArvidsson/andreas-talon/blob/master/core/homophones/homophones.py
import time

from talon import Module

# a list of homophones where each line is a comma separated list
# e.g. where,wear,ware
# a suitable one can be found here:
# https://github.com/pimentel/homophones

mod = Module()

homophones_last_used = {}


@mod.action_class
class Actions:
    def homophones_replace_words(words: list[str]) -> list[str]:
        """Replace words with recently chosen homophones"""
        for i, word in enumerate(words):
            if word in homophones_last_used:
                used = homophones_last_used[word]
                # Reuse homophones used the last 30 minutes
                if time.monotonic() - used["time"] < 30 * 60:
                    used["time"] = time.monotonic()
                    words[i] = used["word"]
        return words
