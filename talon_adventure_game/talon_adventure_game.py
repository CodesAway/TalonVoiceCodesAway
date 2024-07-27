import random

from talon import (
    Context,
    Module,
    actions,
    cron,  # type: ignore
    registry,
    ui,  # type: ignore
)
from talon.canvas import Canvas
from talon.skia import Paint, Rect
from talon.skia.canvas import Canvas as SkiaCanvas

mod = Module()
mod.list("tag_game_command", desc="Commands for Talon Adventure Game")
mod.tag("tag_game", "Playing Talon Adventure Game")

ctx = Context()

tag_game_commands = dict()
tag_game_commands.update(registry.lists["user.letter"][0])
# TODO: move to talon-list (so can read based on which module want to work on)
tag_game_commands["git stage"] = "Add git file contents to the staging area"

tag_game_commands_list = list(tag_game_commands.keys())

ctx.lists["user.tag_game_command"] = tag_game_commands_list

# TODO: make class to store details?
# Reference: community\core\mouse_grid\mouse_grid.py

tag_cron: cron = None
tag_game_last_command: str = ""


def calculate_bottom_border(paint: Paint):
    """Calculates bottom border used for letters which appear below baseline"""
    # Workaround for paint.measure_text, which doesn't factor this in
    letters = ["g", "j", "p", "q", "y"]
    bottom_border = 0

    for letter in letters:
        rect: Rect = paint.measure_text(letter)[1]
        bottom_border = max(bottom_border, rect.y + rect.height)

    return bottom_border


@mod.action_class
class Actions:
    def tag_game_play():
        """Plays Talon Adventure Game (TAG)"""
        ctx.tags = ["user.tag_game"]
        screen = actions.user.screens_get_by_number(1)
        text = tag_game_commands_list[random.randrange(len(tag_game_commands_list))]
        actions.user.tag_game_show_center_text(screen, text)

    def tag_game_stop():
        """Stops Talon Adventure Game (TAG)"""
        global tag_game_last_command

        # TODO: close canvas (once refactor into class)
        ctx.tags = []
        tag_game_last_command = ""

    def tag_game_handle_command(command: str):
        """Handles spoke TAG command"""
        global tag_game_last_command

        if command == tag_game_last_command:
            tag_game_last_command = ""
            command_description = tag_game_commands[command]
            actions.app.notify(f"Command for '{command_description}'")
        else:
            actions.app.notify(f"Incorrect command '{command}'. Please try again.")

    def tag_game_show_center_text(screen: ui.Screen, text: str):
        """Shows text for tag game in center of screen"""
        global tag_game_last_command

        # Reference: community\core\screens\screens.py -> show_screen_number,
        def on_draw(c: SkiaCanvas):
            global tag_cron

            paint: Paint = c.paint

            paint.typeface = "arial"
            # The min(width, height) is to not get gigantic size on portrait screens
            paint.textsize = round(min(c.width, c.height) / 8)

            rect: Rect
            something, rect = paint.measure_text(text)
            bottom_border = calculate_bottom_border(paint)

            x = c.x + c.width / 2 - rect.x - rect.width / 2
            y = c.y + c.height / 2 + rect.height / 2

            border_size = c.paint.textsize / 5

            card_rect = Rect(
                x - border_size,
                y - rect.height - border_size,
                rect.width + 2 * border_size,
                rect.height + 2 * border_size + bottom_border,
            )

            paint.style = paint.Style.FILL
            paint.color = "663399"  # Rebecca purple
            c.draw_rect(card_rect)

            paint.style = paint.Style.FILL
            paint.color = "33b2cd"  # Amy's blue color
            c.draw_text(text, x, y)

            tag_cron = cron.after("3s", canvas.close)

        canvas = Canvas.from_screen(screen)
        canvas.register("draw", on_draw)
        canvas.freeze()
        tag_game_last_command = text
