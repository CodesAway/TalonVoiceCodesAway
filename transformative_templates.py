import json
import re
from collections import deque
from io import StringIO

from talon import Context, Module, actions, storage

from ..andreas_talon.core.imgui import imgui

# TODO: standardize naming - create acronym or something and change everything to use it

mod = Module()
mod.list("codesaway_template_variables", desc="template variables")
# mod.list("stack_template_variables", desc="stack")

variables: dict[str, str] = storage.get("transformative_template_variables", {})

ctx = Context()
# Have the list represent the keys (versus the entry)
# This way, capture will have the key, which can be then used to process
ctx.lists["user.codesaway_template_variables"] = variables.keys()

# Serialize stack like list and then load it as deque (yields expected results)
stack: deque[str] = deque(json.loads(storage.get("stack_template_variables", "")))


# Reference: https://stackoverflow.com/a/61273028
class DequeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, deque):
            return list(obj)

        return json.JSONEncoder.default(self, obj)


# Referenced: screen-spots
@imgui.open(numbered=True)
def gui_list_keys(gui: imgui.GUI):
    global variables

    gui.header("Variables")
    gui.line()

    for i, item in enumerate(variables.items()):
        key = item[0]
        value = item[1]
        if gui.text(f"{key}:\n{value}", clickable=True):
            # TODO: What should clicking on the variable do?
            # Is this even needed?
            print("clicked_num = ", i + 1)
            actions.user.hide_template_variables_list()

    gui.spacer()

    if gui.button("Store close"):
        actions.user.hide_template_variables_list()


@imgui.open(numbered=True)
def draw_stack(gui: imgui.GUI):
    gui.header("Stack")
    gui.line()

    for i, value in enumerate(stack):
        # Show top without number (since number 1 is second element in deque)
        if i == 0:
            if gui.header(f"  0   {value}", clickable=True):
                print("clicked_num = ", i + 1)
        elif gui.text(f"{value}", clickable=True):
            print("clicked_num = ", i + 1)

    gui.spacer()

    if gui.button("Skats"):
        actions.user.hide_template_stack()


def generate_regex(values: dict, transformations: dict) -> str:
    values_list = []
    for item in values.items():
        values_list.append(item)
        # TODO: support transformations
        print(item)

    values_list.sort(reverse=True, key=lambda e: len(e[1]))
    result = StringIO()
    for name, value in values_list:
        if result.tell() != 0:
            result.write("|")

        result.write(f"(?P<{name}>{re.escape(value)})")

    print(values_list)
    regex = result.getvalue()
    print(regex)

    return regex


def replacement(match: re.Match) -> str:
    group_name = [e[0] for e in match.groupdict().items() if e[1] is not None][0]
    return f"@{group_name}@"


# values = {"value1": "ab", "valueA": "a", "value2": "bc"}
# TODO: support transformations
# transformations = {}

# regex = generate_regex(values, transformations)
# text = "a1 bc"
# result = re.sub(regex, replacement, text)

# print("Result:", result)


def backup_template_variables():
    # Update list (otherwise won't see changes to variables)
    ctx.lists["user.codesaway_template_variables"] = variables.keys()
    storage.set("transformative_template_variables", variables)


def backup_template_stack():
    # TODO: errors since deque is not serializable
    # Update list (otherwise won't see changes to variables)
    # ctx.lists["user.codesaway_template_variables"] = variables.keys()
    # storage.set("stack_template_variables", stack)
    stack_json = json.dumps(stack, cls=DequeEncoder)
    print("JSON:", stack_json)
    storage.set("stack_template_variables", stack_json)
    print("backup_template_stack to stack_template_variables")


@mod.action_class
class Actions:
    def store_template_variable(variable: str, value: str) -> None:
        """
        Store template variable
        """
        variables[variable] = value
        backup_template_variables()

    def clear_template_variable(variable: str) -> None:
        """
        Clears template variable
        """
        variables[variable] = ""
        backup_template_variables()

    def clear_all_template_variables() -> None:
        """
        Clears all template variables
        """
        for variable in variables.keys():
            variables[variable] = ""

        backup_template_variables()

    def delete_template_variable(variable: str) -> None:
        """
        Deletes template variable
        """
        del variables[variable]
        backup_template_variables()

    def delete_all_template_variables() -> None:
        """
        Deletes all template variables
        """
        variables.clear()
        backup_template_variables()

    # Referenced: screen-spots
    def show_template_variables_list():
        """Shows a list of existing template variables"""
        gui_list_keys.show()

    def hide_template_variables_list():
        """Hides the list of existing template variables"""
        gui_list_keys.hide()

    def show_template_stack():
        """Shows the stack"""
        draw_stack.show()

    def hide_template_stack():
        """Hides the stack"""
        draw_stack.hide()

    def toggle_template_stack():
        """Toggles the stack"""
        if draw_stack.showing:
            actions.user.hide_template_stack()
        else:
            actions.user.show_template_stack()

    def clear_template_stack():
        """Clear stack"""
        stack.clear()
        backup_template_stack()

    def push_template_stack_list(values: list[str]):
        """Push value on stack"""
        for value in values:
            stack.appendleft(value)

        backup_template_stack()

    def pop_template_stack():
        """Pop value from stack"""
        result = stack.popleft()
        backup_template_stack()
        return result

    def peek_template_stack():
        """Peek at top value of stack"""
        return stack[0]
