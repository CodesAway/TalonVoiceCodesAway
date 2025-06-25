import os
import time
import uuid
from collections import Counter, defaultdict
from pathlib import Path

from talon import (
    actions,
    app,  # type: ignore
    registry,
    ui,  # type: ignore
)

from .talon_adventure_game_metroid import TalonAdventureGameMetroid


# Don't cache since dynamic based on settings changing
def get_tutorial_phrase(tag: TalonAdventureGameMetroid):
    tutorial_phrases = [
        # (
        #     {"continue"},
        #     "Welcome to Talon Adventure Game (TAG) - Metroid-like\nƸ̵̡Ӝ̵̨̄Ʒ→ Say <continue> to continue",
        # ),
        # (
        #     {"help alphabet"},
        #     "First, we'll learn the Talon alphabet, which is a phonetic alphabet\nwhere each letter has a corresponding word.\nƸ̵̡Ӝ̵̨̄Ʒ→ Say <help alphabet> to display the alphabet",
        # ),
        # (
        #     {"help close"},
        #     "Here you can see the Talon alphabet...\nƸ̵̡Ӝ̵̨̄Ʒ→ Say <help close> to close the dialog and continue",
        # ),
        (
            {"continue"},
            "Let's play a game! We'll spell each word, remove it, and for each letter in the word,\ngo to the next word. Repeat until we run out of words.\nThis will help you practice the Talon alphabet.\nƸ̵̡Ӝ̵̨̄Ʒ→ Say <continue> to continue",
        ),
        lambda: tutorial_alpha_start(tag),
        (
            {"continue"},
            "This concludes the tutorial...but the game continues\nWhen you want to stop playing, say <tag stop>\nƸ̵̡Ӝ̵̨̄Ʒ→ Say <continue> to continue",
        ),
    ]

    index = tag.state_index
    if index >= len(tutorial_phrases):
        return None

    tutorial_phrase = tutorial_phrases[index]
    if callable(tutorial_phrase):
        tutorial_phrase = tutorial_phrase()

    return tutorial_phrase

    # Create a menu of different tutorials and add command tag tutorial to allow going through a tutorial
    # TODO: include these in another tutorial about customizing Talon
    # (
    #     {"customize alphabet"},
    #     "We're going to play a little game to help learn and practice the Talon alphabet.\nSay <customize alphabet> to edit the alphabet\n(changes you make are automatically applied)",
    # ),
    # (
    #     {"continue"},
    #     "Once finished making your changes, ensure you save them (so they'll take effect)\nSay <continue> to continue and play the game!",
    # ),


def tutorial_alpha_start(tag: TalonAdventureGameMetroid):
    tutorial_alpha = tag.game_state["tutorial_alpha"]
    return (
        {f"say {word}": True for word in tutorial_alpha}.keys(),
        f"Word list:\n{' '.join(tutorial_alpha)}\nƸ̵̡Ӝ̵̨̄Ʒ→ Say <say `word`> for one of the above words\n(such as <say {next(iter(tutorial_alpha))}> to start playing)",
        set_initial_alpha_word,
    )


def set_initial_alpha_word(tag: TalonAdventureGameMetroid):
    # Get second word (first word is "say")
    tag.game_state["tutorial_alpha_word"] = tag.handle_post_phrase["phrase"][1]
    print(f"Set initial alpha word to {tag.game_state['tutorial_alpha_word']}")


def continue_alpha_game(tag: TalonAdventureGameMetroid):
    tutorial_alpha = tag.game_state["tutorial_alpha"]
    current_word = tag.game_state["tutorial_alpha_word"]
    print(f"Continue alpha game with current word: {current_word}")

    letters = {value: key for key, value in registry.lists["user.letter"][0].items()}
    expected_phrase = " ".join([letters[c] for c in current_word])

    tag.expected_phrases = {expected_phrase}
    tutorial_text = f"Word list:\n{' '.join(tutorial_alpha)}\nƸ̵̡Ӝ̵̨̄Ʒ→ Say <{expected_phrase}> to spell the current word: {current_word})\nƸ̵̡Ӝ̵̨̄Ʒ→ Say <{expected_phrase}> to spell the current word: {current_word})\nƸ̵̡Ӝ̵̨̄Ʒ→ Say <{expected_phrase}> to spell the current word: {current_word})"
    show_tag_tutorial(tag, tutorial_text)

    # TODO: wait for draft widow to be active (seems to be selecting wrong field sometimes)
    actions.sleep(1.0)
    # TODO: calculate anchor based on current_word and tutorial_text
    anchor = "a"
    actions.user.draft_select(anchor)


def start_tutorial(tag: TalonAdventureGameMetroid):
    print(f"In start_tutorial: {tag.game_state=}")
    if "tutorial_alpha" not in tag.game_state:
        tag.game_state["tutorial_alpha"] = minimum_word_span()

    if "tutorial_alpha_word" in tag.game_state:
        continue_alpha_game(tag)
        return

    tutorial_phrase = get_tutorial_phrase(tag)

    if not tutorial_phrase:
        actions.user.draft_hide()
        app.notify(
            "Thank you for playing Talon Adventure Game",
            "...now the real adventure begins",
        )
        return

    tag.expected_phrases = tutorial_phrase[0]
    tutorial_text = tutorial_phrase[1]
    if len(tutorial_phrase) >= 3:
        tag.game_state["victory_callback"] = tutorial_phrase[2]
    # tag.victory_sleep_time = tutorial_phrase[2] if len(tutorial_phrase) >= 3 else 0

    show_tag_tutorial(tag, tutorial_text)


def show_tag_tutorial(tag: TalonAdventureGameMetroid, tutorial_text: str):
    # Actions of "draft show large"
    # actions.user.draft_hide()
    # Added since was getting issues with text not displaying (due to error in logs)
    # TODO: save original size (if possible), so can restore original size when done playing
    actions.user.draft_resize(800, 500)
    actions.user.draft_named_move("middle")
    actions.user.draft_show(tutorial_text)
    # Show done last (which differs from docs) so doesn't have weird graphical glitches when resizing
    actions.sleep(0.3)  # Sleep so context catches up
    tag.expected_app = actions.user.get_running_app("Talon")
    tag.expected_title = "Talon Draft"


def edit_sandbox_file():
    # Use uuid to make file random (so cannot be already open)
    uuid_text = str(uuid.uuid4())
    sandbox_path = Path(
        (os.path.dirname(os.path.realpath(__file__))), f"sandbox {uuid_text}.txt"
    )
    original_window = ui.active_window()
    start_time = time.perf_counter()
    timeout_seconds = 15

    # Create empty file
    sandbox_path.write_text("")
    actions.user.edit_text_file(sandbox_path)
    while ui.active_window() == original_window:
        if time.perf_counter() - start_time > timeout_seconds:
            raise RuntimeError(f"Can't edit text file {sandbox_path}")
        actions.sleep(0.1)

    # Added additional sleep just in case
    actions.sleep(1)
    actions.edit.select_all()
    actions.user.paste("Welcome to Talon Adventure Game - Metroid-like")


TALON_DEFAULT_ALPHABET = {
    "a": "air",
    "b": "bat",
    "c": "cap",
    "d": "drum",
    "e": "each",
    "f": "fine",
    "g": "gust",
    "h": "harp",
    "i": "sit",
    "j": "jury",
    "k": "crunch",
    "l": "look",
    "m": "made",
    "n": "near",
    "o": "odd",
    "p": "pit",
    "q": "quench",
    "r": "red",
    "s": "sun",
    "t": "trap",
    "u": "urge",
    "v": "vest",
    "w": "whale",
    "x": "plex",
    "y": "yank",
    "z": "zip",
}

ENGLISH_LETTERS = "abcdefghijklmnopqrstuvwxyz"


def minimum_word_span() -> list[str]:
    letters = registry.lists["user.letter"][0]
    alphabet_words = defaultdict(set[str])
    word_counts: Counter[str] = Counter()
    unique_words: list[str] = []

    for key, value in letters.items():
        # TODO: for now, limit to English letters (in case other stuff is there)
        # (what changes, if any, are needed to support other characters?)
        if value not in ENGLISH_LETTERS:
            continue

        for letter in key:
            if key in alphabet_words.get(letter, {}):
                continue

            alphabet_words[letter].add(key)
            word_counts[key] += 1

    # Find any missing letters (such as if changed "quench" to "wrench", as a test)
    # TODO: this could be removed if desired, but added to ensure each letter is practiced at least once in the tutorial, regardless of current alphabet
    # (in this example, there would be no 'q' so the 'q' in the user's alphabet wouldn't be ever said nor practiced in the tutorial)
    for letter in ENGLISH_LETTERS:
        if letter in alphabet_words:
            continue

        alphabet_words[letter].add(TALON_DEFAULT_ALPHABET.get(letter))

    unique_letters = [key for key, value in alphabet_words.items() if len(value) == 1]
    for letter in unique_letters:
        unique_word = next(iter(alphabet_words[letter]))
        deleted_words = list(alphabet_words[letter])
        del alphabet_words[letter]
        unique_words.append(unique_word)

        for u in unique_word:
            deleted_words.extend(alphabet_words.pop(u, {}))

        for word in deleted_words:
            word_counts[word] -= 1
            if word_counts[word] == 0:
                del word_counts[word]

    for key, count in word_counts.most_common():
        if not next((u for u in key if u in alphabet_words), None):
            continue

        unique_words.append(key)
        for u in key:
            alphabet_words.pop(u, None)

    return sorted(unique_words)
