import random

from talon import (
    Context,
    Module,
    actions,
    app,  # type: ignore
    registry,
    ui,  # type: ignore
)
from talon.canvas import Canvas
from talon.skia import Paint, Rect
from talon.skia.canvas import Canvas as SkiaCanvas

mod = Module()
mod.list("tag_game_command", "Commands for Talon Adventure Game")
mod.list(
    "tag_game_module",
    "Modules for Talon Adventure Game",
)
mod.list(
    "tag_find_and_replace_commands",
    "Find and Replace commands for Talon Adventure Game",
)
mod.tag("tag_game", "Playing Talon Adventure Game")


@mod.capture(rule="{user.tag_game_module}")
def tag_game_module(m) -> str:
    return m.tag_game_module


ctx = Context()


# Reference: flex-mouse-grid\flex_mouse_grid.py
# Reference: community\core\mouse_grid\mouse_grid.py
class TalonAdventureGame:
    def __init__(self):
        self.screen: ui.Screen = None
        self.canvas: Canvas = None

        self.typeface = "arial"
        self.mono_typeface = "consolas"

        self.background_color = "663399"  # Rebecca purple
        self.text_color = "33b2cd"  # Amy's blue color

        self.last_command = ""
        self.commands: dict[str, str] = dict()
        self.commands_list: list[str]
        self.row_height = 0
        self.bottom_border = 0

        self.tag_playing = False

    def show_game(self, talon_list, include_letters):
        if talon_list:
            self.commands.update(registry.lists[talon_list][0])
            print(f"talon_list: {talon_list}")
            print(registry.lists[talon_list])

        if include_letters or not talon_list:
            self.commands.update(registry.lists["user.letter"][0])

        # TODO: use both commands and coresponding text (similiar to front / back of flashcard)
        self.commands_list = list(self.commands.keys())
        # Makes a copy of all commands
        # (ensures saying a command will not trigger it, such as when practicing, say incorrect command)
        ctx.lists["user.tag_game_command"] = self.commands_list

        self.set_random_command()
        self.tag_playing = True

    def deactivate(self):
        self.tag_playing = False
        self.commands.clear()
        self.last_command = ""

        self.redraw()

    def redraw(self):
        if self.canvas:
            self.canvas.freeze()

    @staticmethod
    def calculate_bottom_border(paint: Paint):
        """Calculates bottom border used for letters which appear below baseline"""
        # Workaround for paint.measure_text, which doesn't factor this in
        letters = ["g", "j", "p", "q", "y"]
        bottom_border = 0

        for letter in letters:
            rect: Rect = paint.measure_text(letter)[1]
            bottom_border = max(bottom_border, rect.y + rect.height)

        return bottom_border

    # Reference: community\core\screens\screens.py -> show_screen_number,
    def on_draw(self, c: SkiaCanvas):
        if not self.tag_playing:
            return

        paint: Paint = c.paint
        paint.typeface = self.mono_typeface
        # The min(width, height) is to not get gigantic size on portrait screens
        paint.textsize = round(min(c.width, c.height) / 8)

        if not self.row_height:
            self.bottom_border = self.calculate_bottom_border(paint)
            sample: Rect = paint.measure_text("A")[1]
            self.row_height = sample.height

        text = self.last_command

        rect: Rect = paint.measure_text(text)[1]
        height = self.row_height

        x = c.x + c.width / 2 - rect.x - rect.width / 2
        y = c.y + c.height / 2 + height / 2 + self.bottom_border / 2
        # actions.user.mouse_move_center_active_window()

        border_size = paint.textsize / 5

        card_rect = Rect(
            x - border_size,
            y - border_size - height,
            rect.width + 2 * border_size,
            height + self.bottom_border + 2 * border_size,
        )

        paint.style = paint.Style.FILL
        paint.color = self.background_color
        c.draw_rect(card_rect)

        paint.style = paint.Style.FILL
        paint.color = self.text_color
        c.draw_text(text, x, y)

    def setup(self):
        # TODO: Initialize via settings
        self.typeface = "arial"
        self.mono_typeface = "consolas"

        self.screen = actions.user.screens_get_by_number(1)

        if self.canvas:
            self.canvas.close()

        self.canvas = Canvas.from_screen(self.screen)
        self.canvas.register("draw", self.on_draw)

        self.canvas.freeze()

    def set_random_command(self):
        if not self.commands_list:
            actions.user.tag_game_stop()
            app.notify(
                "You've practiced all chosen commands. Thanks for playing Talon Adventure Game (TAG)"
            )
            return

        # TODO: instead of getting random, sort initial list and iterate like queue
        # This way, can add chain of commands to practice in order
        index = random.randrange(len(self.commands_list))
        self.last_command = self.commands_list[index]
        del self.commands_list[index]
        self.redraw()

    def handle_command(self, command: str):
        if command == self.last_command:
            # command_description = self.commands[command]
            # actions.app.notify(f"Command for '{command_description}'")
            self.set_random_command()
        else:
            actions.app.notify(f"Incorrect command '{command}'. Please try again.")


tag = TalonAdventureGame()
app.register("ready", tag.setup)


@mod.action_class
class Actions:
    def tag_game_play(talon_list: str = "", include_letters: bool = True):
        """Plays Talon Adventure Game (TAG)"""
        tag.deactivate()
        tag.setup()
        tag.show_game(talon_list, include_letters)

        ctx.tags = ["user.tag_game"]

    def tag_game_stop():
        """Stops Talon Adventure Game (TAG)"""
        tag.deactivate()
        ctx.tags = []

    def tag_game_handle_command(command: str):
        """Handles spoke TAG command"""
        tag.handle_command(command)
