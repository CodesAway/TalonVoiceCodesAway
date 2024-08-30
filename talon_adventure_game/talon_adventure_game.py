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
        bottom_border = max(bottom_border, rect.y + rect.height)

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

        self.typeface = "arial"
        self.command_typeface = "consolas"

        self.background_color = "663399"  # Rebecca purple
        self.text_color = "ffffff"  # Amy's blue color

        self.command_background_color = "663399"  # Rebecca purple
        self.command_text_color = "33b2cd"  # Amy's blue color

        self.last_element: TAGElement = None
        self.commands: set[str] = set()
        self.commands_deque: deque[TAGElement] = deque()

        self.row_height = 0
        self.bottom_border = 0

        self.tag_playing = False
        self.tag_hint = False

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
                        description = value["description"]
                        # self.commands.add(description)
                        del value["description"]
                        value["display_text"] = description

                    element = TAGElement(key, **value)
                    commands_list.append(element)
                    # Add key to prevent accidental commands
                    self.commands.add(key)

                    if element.commands:
                        self.commands.update(element.commands)
                    else:
                        # Add practice for "flip side" display command and say command
                        commands_list.append(TAGElement(key, key, True))
            else:
                talon_list_dict = registry.lists[talon_list][0]
                self.commands.update(talon_list_dict.keys())
                # self.commands.update(talon_list_dict.values())
                for key, value in talon_list_dict.items():
                    commands_list.append(TAGElement(key, value))
                    commands_list.append(TAGElement(key, key, True))

        if include_letters or not self.commands:
            letters = registry.lists["user.letter"][0]
            self.commands.update(letters.keys())
            # self.commands.update(letters.values())
            for key, value in letters.items():
                display_text = "letter " + value
                # TODO: if display text has invalid characters (such as '(' or ')' will show warning in Talon log)
                # self.commands.update(display_text)
                commands_list.append(TAGElement(key, display_text))
                commands_list.append(TAGElement(key, key, True))

        # TODO: use both commands and coresponding text (similiar to front / back of flashcard)
        # Makes a copy of all commands
        # (ensures saying a command will not trigger it, such as when practicing and say incorrect command)
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

    # Reference: community\core\screens\screens.py -> show_screen_number,
    def on_draw(self, c: SkiaCanvas):
        if not self.tag_playing:
            return

        paint: Paint = c.paint
        # TODO: make setting?
        # paint.font.embolden = True
        # The min(width, height) is to not get gigantic size on portrait screens
        paint.textsize = round(min(c.width, c.height) / 8)
        border_size = paint.textsize / 5

        if not self.row_height:
            paint.typeface = self.typeface
            bottom_border = calculate_bottom_border(paint)
            sample: Rect = paint.measure_text("A")[1]
            row_height = sample.height

            paint.typeface = self.command_typeface
            command_bottom_border = calculate_bottom_border(paint)
            sample: Rect = paint.measure_text("A")[1]
            command_row_height = sample.height

            self.bottom_border = (
                bottom_border
                if bottom_border > command_bottom_border
                else command_bottom_border
            )
            self.row_height = (
                row_height if row_height > command_row_height else command_row_height
            )

        paint.typeface = (
            self.command_typeface if self.last_element.is_command else self.typeface
        )

        text = self.last_element.display_text

        # TODO: split text into lines based on width (word wrapping to handle long lines)
        max_line_width = c.width - 2 * border_size

        lines = split_text_into_lines(text, paint, max_line_width)
        line_spacing = border_size
        hint_lines = []

        if self.tag_hint and not self.last_element.is_command:
            hint_lines = split_text_into_lines(
                "`" + self.last_element.name + "`", paint, max_line_width
            )
            lines = hint_lines + lines

        between_lines_height = self.bottom_border + line_spacing
        height = self.row_height * len(lines) + between_lines_height * (len(lines) - 1)

        # rect: Rect = paint.measure_text(text)[1]
        rects: list[Rect] = [paint.measure_text(line)[1] for line in lines]
        min_x = min(rects, key=attrgetter("x")).x
        max_width = max(rects, key=attrgetter("width")).width

        # x = c.x + c.width / 2 - rect.x - rect.width / 2
        x = c.x + c.width / 2 - min_x - max_width / 2
        y = c.y + c.height / 2 + height / 2 + self.bottom_border / 2

        card_rect = Rect(
            x - border_size,
            y - border_size - height,
            # rect.width + 2 * border_size,
            max_width + 2 * border_size,
            height + self.bottom_border + 2 * border_size,
        )

        paint.style = paint.Style.FILL
        paint.color = (
            self.command_background_color
            if self.last_element.is_command
            else self.background_color
        )
        c.draw_rect(card_rect)

        paint.style = paint.Style.FILL

        for index, line in enumerate(lines):
            if index < len(hint_lines):
                paint.color = self.command_text_color
            else:
                paint.color = (
                    self.command_text_color
                    if self.last_element.is_command
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

        active_modes = scope.get("mode")
        if "user.tag_game" in active_modes:
            actions.mode.disable("user.tag_game")

            if (
                "command" not in active_modes
                and "dictation" not in active_modes
                and "sleep" not in active_modes
            ):
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
