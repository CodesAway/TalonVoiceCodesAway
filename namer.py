import re
from io import StringIO

from talon import Context, Module, actions, storage

# TODO: replace with standard imgui (or use try block to allow either)
from ..andreas_talon.core.imgui import imgui

mod = Module()
mod.list("namer_variable", desc="namer variables")

namer_variables: dict[str, str] = storage.get("namer.variables", {})

ctx = Context()
# Have the list represent the keys (versus the entry)
# This way, capture will have the key, which can be then used to process
ctx.lists["user.namer_variable"] = namer_variables.keys()


@imgui.open(numbered=True)
def gui_namer_variables(gui: imgui.GUI):
    gui.header("Variables")
    gui.line()

    for i, item in enumerate(namer_variables.items()):
        variable = item[0]
        value = item[1]
        if gui.text(f"{variable}:\n{value}", clickable=True):
            # TODO: What should clicking on the variable do?
            # Is this even needed?
            print("clicked_num = ", i + 1)
            actions.user.hide_namer_variables()

    gui.spacer()

    if gui.button("Namer"):
        actions.user.hide_namer_variables()


def backup_namer_variables():
    # Update list (otherwise won't see changes to variables)
    ctx.lists["user.namer_variable"] = namer_variables.keys()
    storage.set("namer.variables", namer_variables)


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


# TODO: write logic to use namer variables to generate snippets
# values = {"value1": "ab", "valueA": "a", "value2": "bc"}
# TODO: support transformations
# transformations = {}

# regex = generate_regex(values, transformations)
# text = "a1 bc"
# result = re.sub(regex, replacement, text)

# print("Result:", result)


@mod.action_class
class Actions:
    def hide_namer_variables():
        """Hides the GUI for namer variables"""
        gui_namer_variables.hide()

    def show_namer_variables():
        """Shows the GUI for namer variables"""
        gui_namer_variables.show()

    def toggle_namer_variables():
        """Toggles the GUI for namer variables"""
        if gui_namer_variables.showing:
            actions.user.hide_namer_variables()
        else:
            actions.user.show_namer_variables()

    def set_namer_variable(variable: str, value: str) -> None:
        """
        Sets namer variable
        """
        namer_variables[variable] = value
        backup_namer_variables()

    def clear_namer_variable(variable: str) -> None:
        """
        Clears namer variable (sets to blank)
        """
        namer_variables[variable] = ""
        backup_namer_variables()

    def clear_all_namer_variables() -> None:
        """
        Clears all namer variables (sets to blank)
        """
        for variable in namer_variables.keys():
            namer_variables[variable] = ""

        backup_namer_variables()

    def delete_namer_variable(variable: str) -> None:
        """
        Deletes namer variable
        """
        del namer_variables[variable]
        backup_namer_variables()

    def delete_all_namer_variables() -> None:
        """
        Deletes all namer variables
        """
        namer_variables.clear()
        backup_namer_variables()
