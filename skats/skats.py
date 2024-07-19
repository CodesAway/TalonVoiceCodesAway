import json
import logging
from collections import deque

from talon import (
    Module,
    actions,
    imgui,  # type: ignore
    storage,
)

mod = Module()

# Serialize stack like list (in DequeEncoder)
# Then, load it as deque (yields expected results)
skats_stack: deque[str] = deque(json.loads(storage.get("skats.stack", "{}")))


# Reference: https://stackoverflow.com/a/61273028
class DequeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, deque):
            return list(obj)

        return json.JSONEncoder.default(self, obj)


@imgui.open()
def gui_skats_stack(gui: imgui.GUI):
    gui.text("Stack")
    gui.line()

    for i, value in enumerate(skats_stack):
        # TODO: Reference https://github.com/AndreasArvidsson/andreas-talon/blob/master/core/imgui.py
        # Handle multi-line and long text
        gui.text(f"{i:2d}   {value}")

    gui.spacer()

    if gui.button("Skats"):
        actions.user.hide_skats_stack()


def backup_skats_stack():
    skats_stack_json = json.dumps(skats_stack, cls=DequeEncoder)
    storage.set("skats.stack", skats_stack_json)


@mod.action_class
class Actions:
    def hide_skats_stack():
        """Hides the GUI for skats stack"""
        gui_skats_stack.hide()

    def show_skats_stack():
        """Shows the GUI for skats stack"""
        gui_skats_stack.show()

    def toggle_skats_stack():
        """Toggles the GUI for skats stack"""
        if gui_skats_stack.showing:
            actions.user.hide_skats_stack()
        else:
            actions.user.show_skats_stack()

    def clear_skats_stack():
        """Clear stack"""
        skats_stack.clear()
        backup_skats_stack()

    def delete_skats_stack_index(index: int):
        """Delete value at index from stack"""
        del skats_stack[index]
        backup_skats_stack()

    def push_skats_stack(value: str):
        """Push value on top of stack"""
        skats_stack.appendleft(value)
        backup_skats_stack()

    def push_skats_stack_list(values: list[str]):
        """Push value on stack"""
        # Iterate in reverse order so 0th element in list will be at top
        for value in reversed(values):
            skats_stack.appendleft(value)

        backup_skats_stack()

    def push_skats_stack_index_list(index: int, values: list[str]):
        """Push values on stack at index"""
        if index > len(skats_stack):
            logging.debug(
                f"index: {index} is out of bounds of stack with size {len(skats_stack)}"
            )
            return
        elif index == len(skats_stack):
            # Append to end
            for value in values:
                skats_stack.append(value)

            backup_skats_stack()
            return

        skats_stack.rotate(-index)

        # Iterate in reverse order so 0th element in list will be at top
        for value in reversed(values):
            skats_stack.appendleft(value)

        skats_stack.rotate(index)
        backup_skats_stack()

    def pop_skats_stack():
        """Pop top value from stack"""
        result = skats_stack.popleft()
        backup_skats_stack()
        return result

    def pop_skats_stack_index(index: int):
        """Pop value at index from stack"""
        result = skats_stack[index]
        del skats_stack[index]
        backup_skats_stack()
        return result

    def peek_skats_stack():
        """Peek top value of stack"""
        return skats_stack[0]

    def peek_skats_stack_index(index: int):
        """Peek value at index of stack"""
        return skats_stack[index]

    def dig_skats_stack(index: int):
        """Moves value at index to top of stack"""
        value = skats_stack[index]
        del skats_stack[index]
        actions.user.push_skats_stack(value)
