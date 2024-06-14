import re

from talon import Context, Module, actions, storage

# TODO: replace with standard imgui (or use try block to allow either)
from ..andreas_talon.core.imgui import GUI, ImGUI
from ..community.core.snippets.snippet_types import Snippet

mod = Module()
mod.list("namer_variable", desc="namer variables")


namer_variables: dict[str, str] = storage.get("namer.variables", {})

ctx = Context()
# Have the list represent the keys (versus the entry)
# This way, capture will have the key, which can be then used to process
ctx.lists["user.namer_variable"] = namer_variables.keys()


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
    # Update list (otherwise won't see changes to variables)
    ctx.lists["user.namer_variable"] = namer_variables.keys()
    storage.set("namer.variables", namer_variables)


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

    def set_namer_variable(variable: str, value: str) -> None:
        """
        Sets namer variable
        """
        # TODO: should namer_variables be sorted for ease of reference?
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

    # Based on community\core\snippets\snippets_insert.py -> insert_snippet_by_name
    def insert_snippet_via_namer(name: str):
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
