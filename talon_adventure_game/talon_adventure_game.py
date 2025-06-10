import json
import os.path
import random
from collections import deque
from dataclasses import dataclass
from operator import attrgetter

from talon import (
    Context,
    Module,
    actions,
    app,  # type: ignore
    registry,
    scope,
    ui,  # type: ignore
)
from talon.canvas import Canvas
from talon.skia import Canvas as SkiaCanvas
from talon.skia import Paint, Rect

mod = Module()
mod.list("tag_game_command", "Commands for Talon Adventure Game")
mod.list(
    "tag_game_module",
    "Modules for Talon Adventure Game",
)
mod.mode("tag_game", "Playing Talon Adventure Game")


@mod.capture(rule="{user.tag_game_module}")
def tag_game_module(m) -> str:
    return m.tag_game_module


ctx = Context()


def is_non_empty_str(value: any):
    return value and isinstance(value, str)


@dataclass
class TAGElement:
    name: str
    display_text: str
    is_command: bool = False

    # None unless represents a flow / chain of commands (specified in JSON)
    commands: list[str] = None

    def __post_init__(self):
        if not is_non_empty_str(self.name):
            raise TypeError(f"name must be a non-empty str, yet has value: {self.name}")

        if not is_non_empty_str(self.display_text):
            raise TypeError(
                f"display_text of '{self.name}' must be a non-empty str, yet has value: {self.display_text}"
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


def calculate_bottom_border(paint: Paint):
    """Calculates bottom border used for letters which appear below baseline"""
    # Workaround for paint.measure_text, which doesn't factor this in
    letters = ["g", "j", "p", "q", "y"]
    bottom_border = 0

    for letter in letters:
        rect: Rect = paint.measure_text(letter)[1]
        bottom_border = max(bottom_border, rect.bot)

    return bottom_border


def split_text_into_lines(text: str, paint: Paint, max_line_width: int) -> list[str]:
    # Reference: https://github.com/chaosparrot/talon_hud/blob/master/utils.py -> layout_rich_text
    # TODO: handle if single word is longer than max_line_width

    words = text.split()

    if len(words) == 1:
        return [text]

    current_words = []
    lines = []

    for word in words:
        current_words.append(word)
        width = paint.measure_text(" ".join(current_words))[1].width

        if width > max_line_width:
            # Last word made too long
            current_words.pop()
            lines.append(" ".join(current_words))
            current_words = [word]

    # Add final line
    lines.append(" ".join(current_words))

    return lines


# Reference: flex-mouse-grid\flex_mouse_grid.py
# Reference: community\core\mouse_grid\mouse_grid.py
class TalonAdventureGame:
    def __init__(self):
        self.screen: ui.Screen = None
        self.canvas: Canvas = None

        # TODO: Initialize via settings
        self.typeface = "arial"
        self.command_typeface = "consolas"

        # TODO: Initialize via settings
        self.background_color = "663399"  # Rebecca purple
        self.text_color = "ffffff"  # White

        # TODO: Initialize via settings
        self.command_background_color = "663399"  # Rebecca purple
        self.command_text_color = "33b2cd"  # Amy's blue color

        self.last_element: TAGElement = None
        self.commands: set[str] = set()
        self.commands_deque: deque[TAGElement] = deque()

        self.row_height = 0
        self.bottom_border = 0

        self.tag_playing = False
        self.tag_hint = False

    def populate_commands_from_json(self, talon_list: str):
        cwd = os.path.dirname(os.path.realpath(__file__))
        pathname = os.path.join(cwd, os.path.expandvars(talon_list))
        with open(pathname) as file:
            json_commands = json.load(file)

        commands_list: list[TAGElement] = []
        value: dict[str, any]
        for key, value in json_commands.items():
            if key == "":
                # NOTE: can use empty key to specify file which is being done (since JSON doesn't allow comments)
                continue

            if isinstance(value, str):
                value = {"display_text": value}
            elif isinstance(value, list):
                # NOTE: display_text is not used when there are commands, so just use key to pass validations
                value = {"commands": value, "display_text": key}
            elif value.get("description"):
                value["display_text"] = value.pop("description")

            element = TAGElement(key, **value)
            commands_list.append(element)
            # Add key to prevent accidental commands
            self.commands.add(key)

            if element.commands:
                self.commands.update(element.commands)
            else:
                # Add practice for "flip side" display command and say command
                commands_list.append(TAGElement(key, key, True))

        return commands_list

    def populate_commands(self, talon_list: str) -> list[TAGElement]:
        # TODO: optionally support having multiple lists / json defined using "|" as delimiter
        # Could also allow referencing other map keys from the tag_game_module.talon-list
        # (so could specify once and then combine to practice several together)
        if talon_list:
            if talon_list.endswith(".json"):
                return self.populate_commands_from_json(talon_list)
            else:
                talon_list_dict = registry.lists[talon_list][0]
                self.commands.update(talon_list_dict.keys())
                return [
                    e
                    for key, value in talon_list_dict.items()
                    for e in (TAGElement(key, value), TAGElement(key, key, True))
                ]
        else:
            return []

    def show_game(self, talon_list: str, include_letters: bool):
        # TODO: if display text has invalid characters (such as '(' or ')' will show warning in Talon log)
        commands_list: list[TAGElement] = self.populate_commands(talon_list)

        if include_letters or not self.commands:
            letters = registry.lists["user.letter"][0]
            self.commands.update(letters.keys())
            for key, value in letters.items():
                commands_list.append(TAGElement(key, "letter " + value))
                commands_list.append(TAGElement(key, key, True))

        ctx.lists["user.tag_game_command"] = self.commands
        random.shuffle(commands_list)
        self.commands_deque = deque(commands_list)

        self.set_next_command()
        self.tag_playing = True

    def deactivate(self):
        self.tag_hint = False
        self.tag_playing = False
        self.commands_deque.clear()
        self.commands.clear()
        self.last_element = None

        self.redraw()

    def redraw(self):
        if self.canvas:
            self.canvas.freeze()

    @staticmethod
    def calc_row_height(paint: Paint, typeface: str):
        # TODO: tried to restore original typeface, but if None get error "invalid type for typeface"
        paint.typeface = typeface
        bottom_border = calculate_bottom_border(paint)
        row_height = paint.measure_text("A")[1].height

        return (row_height, bottom_border)

    def is_command(self):
        return self.last_element.is_command

    def determine_lines(
        self, paint: Paint, max_line_width: int
    ) -> tuple[list[str], int]:
        lines = [
            line
            for split_line in self.last_element.display_text.split("\n")
            for line in split_text_into_lines(split_line, paint, max_line_width)
        ]

        hint_lines = []
        if self.tag_hint and not self.is_command():
            hint_lines = split_text_into_lines(
                "`" + self.last_element.name + "`", paint, max_line_width
            )
            lines = hint_lines + lines

        return (lines, len(hint_lines))

    # Reference: community\core\screens\screens.py -> show_screen_number,
    def on_draw(self, c: SkiaCanvas):
        if not self.tag_playing:
            return

        paint: Paint = c.paint
        # The min(width, height) is to not get gigantic size on portrait screens
        paint.textsize = round(min(c.width, c.height) / 8)
        border_size = round(paint.textsize / 5)

        if not self.row_height:
            self.row_height, self.bottom_border = max(
                self.calc_row_height(paint, self.typeface),
                self.calc_row_height(paint, self.command_typeface),
            )

        paint.typeface = self.command_typeface if self.is_command() else self.typeface
        lines, hint_lines_count = self.determine_lines(paint, c.width - 2 * border_size)

        between_lines_height = self.bottom_border + border_size
        height = self.row_height * len(lines) + between_lines_height * (len(lines) - 1)

        rects: list[Rect] = [c.paint.measure_text(line)[1] for line in lines]
        min_x = min(rects, key=attrgetter("x")).x
        max_width = max(rects, key=attrgetter("width")).width

        x = c.x + c.width / 2 - min_x - max_width / 2
        y = c.y + c.height / 2 + height / 2 + self.bottom_border / 2

        card_rect = Rect(
            x - border_size,
            y - border_size - height,
            max_width + 2 * border_size,
            height + self.bottom_border + 2 * border_size,
        )

        paint.style = paint.Style.FILL
        paint.color = (
            self.command_background_color
            if self.is_command()
            else self.background_color
        )
        c.draw_rect(card_rect)

        for index, line in enumerate(lines):
            paint.color = (
                self.command_text_color
                if index < hint_lines_count or self.is_command()
                else self.text_color
            )

            c.draw_text(
                line,
                x,
                y - (len(lines) - 1 - index) * (self.row_height + between_lines_height),
            )

    def setup(self):
        # TODO: Initialize via settings
        self.typeface = "arial"
        self.command_typeface = "consolas"

        # Workaround for this script being modified while TAG is running (otherwise Talon left in weird state)
        active_modes: set = scope.get("mode")
        if "user.tag_game" in active_modes:
            actions.mode.disable("user.tag_game")

            if not active_modes.intersection({"command", "dictation", "sleep"}):
                actions.mode.enable("command")

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

        last_element = self.commands_deque.popleft()

        if last_element.commands:
            # Push each command (push in reverse order to maintain order of commands, since push like stack)
            for command in reversed(last_element.commands):
                self.commands_deque.appendleft(TAGElement(command, command, True))

            last_element = self.commands_deque.popleft()

        self.last_element = last_element
        self.redraw()

    def handle_command(self, command: str):
        if self.last_element and command == self.last_element.name:
            self.tag_hint = False
            self.set_next_command()
        else:
            app.notify(f"Incorrect command '{command}'. Please try again.")


tag = TalonAdventureGame()
app.register("ready", tag.setup)


@mod.action_class
class Actions:
    def tag_game_play(talon_list: str = "", include_letters: bool = True):
        """Plays Talon Adventure Game (TAG)"""
        tag.deactivate()
        tag.setup()
        tag.show_game(talon_list, include_letters)

        actions.mode.disable("command")
        actions.mode.enable("user.tag_game")

    def tag_game_stop():
        """Stops Talon Adventure Game (TAG)"""
        tag.deactivate()
        actions.mode.enable("command")
        actions.mode.disable("user.tag_game")

    def tag_game_hint():
        """Shows command corresponding to description"""
        tag.tag_hint = not tag.tag_hint
        tag.redraw()

    def tag_game_handle_command(command: str):
        """Handles spoke TAG command"""
        tag.handle_command(command.strip())
