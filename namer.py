import re
from io import StringIO

from talon import Module, actions, clip, storage

# TODO: replace with standard imgui (or use try block to allow either)
from ..andreas_talon.core.imgui import GUI, ImGUI
from ..community.core.snippets.snippet_types import Snippet

mod = Module()


namer_variables: dict[str, str] = storage.get("namer.variables", {})
namer_variables_keys = list(namer_variables.keys())
# TODO: support user defined transformations (via methods)
transformations = []


@ImGUI.open(numbered=True)
def gui_namer_variables(gui: GUI):
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
    global namer_variables_keys
    storage.set("namer.variables", namer_variables)
    namer_variables_keys = list(namer_variables.keys())


def namer_snip_replacement(values: dict, transformations: dict, body: str) -> str:
    values_list = []
    for variable in namer_variables_keys:
        # Skip empty values (since not part of snippet replacement)
        if namer_variables[variable] == "":
            continue

        values_list.append(variable)
        # TODO: support transformations

    values_list.sort(reverse=True, key=lambda e: len(namer_variables[e]))
    result = StringIO()
    # TODO: change into `"|".join(list comphension)``
    for variable in values_list:
        if result.tell() != 0:
            result.write("|")

        value = namer_variables[variable]
        result.write(f"({re.escape(value)})")

    # print(values_list)
    regex = result.getvalue()
    # print(regex)

    def replacement(match: re.Match) -> str:
        # print("groups:", match.groups())

        group_index = [
            index for index, value in enumerate(match.groups()) if value is not None
        ][0]
        # print("group_index:", group_index)

        group_name = values_list[group_index]
        # print("replacement:", group_name)

        return f"${{{group_name}}}"

    result = re.sub(regex, replacement, body)
    return result


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

    # TODO: Need way to get variables so can filter and search for them
    def get_namer_variable(variable: str):
        """Gets namer variable"""
        return namer_variables[variable]

    def set_namer_variable(variable: str, value: str) -> None:
        """
        Sets namer variable
        """
        # TODO: should namer_variables be sorted for ease of reference?
        namer_variables[variable] = value
        backup_namer_variables()

    def strip_namer_variable(variable: str):
        """Strips namer variable (removes leading / trailing whitespace)"""
        namer_variables[variable] = namer_variables[variable].strip()
        backup_namer_variables()

    def copy_namer_variable(variable: str):
        """Copies current text to clipboard and sets as namer variable"""

        # Workaround, since using actions.edit.copy() seemed to have timing issue (had old clipboard contents stored)
        value = actions.edit.selected_text()
        clip.set_text(value)

        actions.user.clipboard_namer_variable(variable)

    def clipboard_namer_variable(variable: str):
        """Sets namer variable to clipboard contents"""
        value = clip.text()
        actions.user.set_namer_variable(variable, value)

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

    # Based on community\core\snippets\snippets_insert.py -> insert_snippet_by_name
    def namer_insert_snippet(name: str):
        """Insert snippet <name>"""
        snippet: Snippet = actions.user.get_snippet(name)
        body = snippet.body

        if namer_variables:
            # TODO: alter to look through once and get replacement body (handling transformations)
            for k, v in namer_variables.items():
                reg = re.compile(rf"\${k}|\$\{{{k}\}}")
                if not reg.search(body):
                    # raise ValueError(
                    #     f"Can't substitute non existing variable '{k}' in snippet '{name}'"
                    # )
                    continue
                body = reg.sub(v, body)

        actions.user.insert_snippet(body)

    def namer_make_snippet(name: str, body: str):
        """Makes snippet"""
        result = namer_snip_replacement(namer_variables, transformations, body)

        print("namer_make_snippet:")
        print(result)
