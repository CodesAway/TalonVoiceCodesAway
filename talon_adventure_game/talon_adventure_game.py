import json
import os.path
import random
from collections import deque
from dataclasses import dataclass

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


def is_non_empty_str(value: any):
    return value and isinstance(value, str)


@dataclass
class TAGElement:
    name: str
    description: str
    commands: list[str] = (
        None  # None unless represents a flow / chain of commands (specified in JSON)
    )

    def __post_init__(self):
        if not is_non_empty_str(self.name):
            raise TypeError(f"name must be a non-empty str, yet has value: {self.name}")

        if not is_non_empty_str(self.description):
            raise TypeError(
                f"description of '{self.name}' must be a non-empty str, yet has value: {self.description}"
            )

        if self.commands is not None:
            if not isinstance(self.commands, list):
                raise TypeError(
                    f"commands of '{self.name}' should be an optional list, yet has value: {self.commands}"
                )

            if not all(is_non_empty_str(e) for e in self.commands):
                raise TypeError(
                    f"commands of '{self.name}' should be an optional list[str] with non-empty values, yet has value: {self.commands}"
                )


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
        self.commands: set[str] = set()
        self.commands_deque: deque[TAGElement] = deque()

        self.row_height = 0
        self.bottom_border = 0

        self.tag_playing = False

    def show_game(self, talon_list: str, include_letters: bool):
        commands_list: list[TAGElement] = []
        if talon_list:
            # TODO: optionally support having multiple lists / json defined using "|" as delimiter
            # Could also allow referencing other map keys from the tag_game_module.talon-list
            # (so could specify once and then combine to practice several together)
            if talon_list.endswith(".json"):
                cwd = os.path.dirname(os.path.realpath(__file__))
                pathname = os.path.join(cwd, os.path.expandvars(talon_list))
                with open(pathname) as file:
                    json_commands = json.load(file)

                for key, value in json_commands.items():
                    element = TAGElement(key, **value)
                    commands_list.append(element)
                    self.commands.add(key)
            else:
                talon_list_dict = registry.lists[talon_list][0]
                self.commands.update(talon_list_dict.keys())
                for key, value in talon_list_dict.items():
                    commands_list.append(TAGElement(key, value))

        if include_letters or not self.commands:
            letters = registry.lists["user.letter"][0]
            self.commands.update(letters.keys())
            for key, value in letters.items():
                commands_list.append(TAGElement(key, value))

        # TODO: use both commands and coresponding text (similiar to front / back of flashcard)
        # Makes a copy of all commands
        # (ensures saying a command will not trigger it, such as when practicing and say incorrect command)
        ctx.lists["user.tag_game_command"] = self.commands
        random.shuffle(commands_list)
        self.commands_deque = deque(commands_list)

        self.set_next_command()
        self.tag_playing = True

    def deactivate(self):
        self.tag_playing = False
        self.commands_deque.clear()
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

    def set_next_command(self):
        if not self.commands_deque:
            actions.user.tag_game_stop()
            app.notify(
                "Practice complete",
                body="Thanks for playing Talon Adventure Game (TAG)!",
            )
            return

        self.last_command = self.commands_deque.popleft().name
        self.redraw()

    def handle_command(self, command: str):
        if command == self.last_command:
            self.set_next_command()
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
