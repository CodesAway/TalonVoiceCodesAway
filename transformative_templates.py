import re
from io import StringIO

from talon import Context, Module, actions, storage

from ..andreas_talon.core.imgui import imgui

# TODO: standardize naming - create acronym or something and change everything to use it

mod = Module()
mod.list("codesaway_template_variables", desc="template variables")

variables: dict[str, str] = storage.get("transformative_template_variables", {})

ctx = Context()
# Have the list represent the keys (versus the entry)
# This way, capture will have the key, which can be then used to process
ctx.lists["user.codesaway_template_variables"] = variables.keys()


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
