from talon import (
    Context,
    Module,
    actions,
    app,  # type: ignore
    speech_system,
    ui,  # type: ignore
)
from talon.grammar import Phrase

from ..andreas_talon.analyze_phrase.analyze_phrase import analyze_phrase

ctx = Context()

mod = Module()
mod.tag("tag_metroid", "Playing Talon Adventure Game - Metroid-like")


class TalonAdventureGameMetroid:
    def __init__(self):
        self.tag_playing = False
        self.expected_phrases: set[str] = set()
        self.expected_app: ui.App = None
        self.expected_title: str = ""
        # TODO: save and load this...reference namer)
        self.game_state: dict[str, any] = {}
        # TODO: morph this into a scalable idea in game_state
        self.state_index: int = 0
        # self.victory_sleep_time: float = 0
        self.handle_post_phrase: Phrase = None

    def show_game(self):
        tag.tag_playing = True

        self.continue_game()
        # edit_sandbox_file()

    def clear_expected_phrases(self):
        self.expected_phrases = set()
        self.expected_app = None
        self.expected_title = ""

    def deactivate(self):
        self.tag_playing = False
        self.clear_expected_phrases()
        self.state_index = 0
        actions.user.draft_hide()

    def setup(self):
        speech_system.register("pre:phrase", pre_phrase)
        speech_system.register("post:phrase", post_phrase)

    def set_next_step(self):
        victory_callback = self.game_state.get("victory_callback")
        if callable(victory_callback):
            victory_callback(self)

        tag.state_index += 1
        print(f"New state index: {tag.state_index}")
        tag.handle_post_phrase = None

        # if tag.victory_sleep_time:
        #     actions.sleep(tag.victory_sleep_time)

        self.continue_game()

    def continue_game(self):
        # TODO: do import based on where at in game
        # (added import here to prevent cyclic dependency when put tutorials in separate files)
        from .tag_metroid_tutorial import start_tutorial

        start_tutorial(self)


tag = TalonAdventureGameMetroid()
# app.register("ready", tag.setup)


def pre_phrase(phrase: Phrase):
    if not phrase["phrase"]:
        return

    print(f"TAG Metroid phrase: {' '.join(phrase['phrase'])}")

    if "parsed" in phrase:
        # Get an analyzed phrase
        analyzed_phrase = analyze_phrase(phrase)
        commands = analyzed_phrase.commands
        print(f"Command count: {len(commands)}")

    # Necessary, otherwise can never stop if expecting a phrase
    if " ".join(phrase["phrase"]) == "tag stop":
        return

    if tag.expected_phrases:
        handle_expected_phrase(phrase)
        return

    # for command in commands:a
    #     print(command)

    # Pretty print analyzed phrase
    # TODO: investigate (see what info can pbe used for my needs)
    # pretty_print_phrase(analyzed_phrase)


def post_phrase(phrase: Phrase):
    if phrase == tag.handle_post_phrase:
        tag.set_next_step()
        tag.game_state.pop("victory_callback", None)


def handle_expected_phrase(phrase: Phrase):
    words = phrase["phrase"]
    if len(words) == 0:
        return

    if type(words) is not list:
        words = list(words)

    active_app = ui.active_app()
    app_matches = active_app == tag.expected_app if tag.expected_app else True
    title_matches = (
        active_app.active_window.title == tag.expected_title
        if tag.expected_title
        else True
    )

    words_text = " ".join(words)
    words_match = words_text in tag.expected_phrases

    if words_match and app_matches and title_matches:
        # TODO: may have an action to do, such as when play Talon alphabet game

        tag.clear_expected_phrases()
        # tag.set_next_step()
        tag.handle_post_phrase = phrase
        return

    cancel_entire_phrase(phrase)
    if words_match:
        error_message = f'TAG Metroid:\nIgnoring "{words_text}"\n(wrong window has focus...switching focus)'
    elif len(tag.expected_phrases) == 1:
        error_message = f'TAG Metroid:\nIgnoring "{words_text}"\n(expected "{next(iter(tag.expected_phrases))}")'
    else:
        error_message = f'TAG Metroid:\nIgnoring "{words_text}"\n(expected one of {str(list(tag.expected_phrases)).removeprefix("[").removesuffix("]")})'

    print(error_message)
    app.notify(error_message)

    if words_match:
        # Find window in app that matches the title
        window = next(
            (a for a in tag.expected_app.windows() if a.title == tag.expected_title),
            tag.expected_app.active_window,
        )

        # Change focus to expected app (might still be wrong window, but not sure if need better logic)
        actions.user.switcher_focus_window(window)


# Source: %appdata%\talon\user\community\plugin\cancel\cancel.py
def cancel_entire_phrase(phrase: Phrase):
    phrase["phrase"] = []
    if "parsed" in phrase:
        phrase["parsed"]._sequence = []


@mod.action_class
class Actions:
    def tag_metroid_play():
        """Plays Talon Adventure Game (TAG) - Metroid-like"""
        ctx.tags = ["user.tag_metroid"]
        tag.deactivate()
        tag.setup()
        tag.show_game()

    def tag_metroid_stop():
        """Stops Talon Adventure Game (TAG) - Metroid-like"""
        speech_system.unregister("pre:phrase", pre_phrase)
        speech_system.unregister("post:phrase", post_phrase)
        tag.deactivate()
        tag.game_state.clear()
        ctx.tags = []
