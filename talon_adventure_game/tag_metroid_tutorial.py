import os
import time
import uuid
from pathlib import Path

from talon import (
    actions,
    app,  # type: ignore
    ui,  # type: ignore
)

from .talon_adventure_game_metroid import TalonAdventureGameMetroid


# Don't cache since dynamic based on settings changing
def get_tutorial_phrases():
    return [
        (
            {"continue"},
            "Welcome to Talon Adventure Game (TAG) - Metroid-like\nƸ̵̡Ӝ̵̨̄Ʒ→ Say <continue> to continue",
        ),
        # TODO: get these dynamically (so can play with their alphabet)
        (
            {"help alphabet"},
            "First, we'll learn the Talon alphabet, which is a phonetic alphabet\nwhere each letter has a corresponding word.\nƸ̵̡Ӝ̵̨̄Ʒ→ Say <help alphabet> to display the alphabet",
        ),
        (
            {"help close"},
            "Here you can see the Talon alphabet...\nƸ̵̡Ӝ̵̨̄Ʒ→ Say <help close> to close the dialog and continue",
        ),
        # TODO: download a fresh copy of Talon / community to verify the file shows the correct location for suggested customizations
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
        (
            {"continue"},
            "This concludes the tutorial...but the game continues\nWhen you want to stop playing, say <tag stop>\nƸ̵̡Ӝ̵̨̄Ʒ→ Say <continue> to continue",
        ),
    ]


def start_tutorial(tag: TalonAdventureGameMetroid):
    index = tag.state_index
    tutorial_phrases = get_tutorial_phrases()

    if index >= len(tutorial_phrases):
        actions.user.draft_hide()
        app.notify(
            "Thank you for playing Talon Adventure Game",
            "...now the real adventure begins",
        )
        return

    tutorial_phrase = tutorial_phrases[index]
    tag.expected_phrases = tutorial_phrase[0]
    tutorial_text = tutorial_phrase[1]
    tag.victory_sleep_time = tutorial_phrase[2] if len(tutorial_phrase) >= 3 else 0

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
