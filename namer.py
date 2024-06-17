import logging
import re
from io import StringIO
from pathlib import Path

from talon import Context, Module, actions, clip, settings, storage

# TODO: replace with standard imgui (or use try block to allow either)
from ..andreas_talon.core.imgui import GUI, ImGUI
from ..community.core.snippets.snippet_types import Snippet

mod = Module()
mod.list("namer_variable", "namer variables")

ctx = Context()

namer_variables: dict[str, str] = storage.get("namer.variables", {})
namer_variables_keys = list(namer_variables.keys())
ctx.lists["user.namer_variable"] = namer_variables_keys

# TODO: support user defined transformations (via methods)
transformations = {}


@ImGUI.open(numbered=True)
def namer_gui_variables(gui: GUI):
    gui.header("Variables")
    gui.line()

    for i, item in enumerate(namer_variables.items()):
        variable = item[0]
        value = item[1]
        if gui.text(f"{variable}:\n{value}", clickable=True):
            # TODO: What should clicking on the variable do?
            # Is this even needed?
            logging.debug("clicked_num = ", i + 1)
            actions.user.namer_hide_variables()

    gui.spacer()

    if gui.button("Namer"):
        actions.user.namer_hide_variables()


def namer_backup_variables():
    global namer_variables_keys
    storage.set("namer.variables", namer_variables)
    namer_variables_keys = list(namer_variables.keys())
    ctx.lists["user.namer_variable"] = namer_variables_keys


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
    def namer_hide_variables():
        """Hides the GUI for namer variables"""
        namer_gui_variables.hide()

    def namer_show_variables():
        """Shows the GUI for namer variables"""
        namer_gui_variables.show()

    def namer_toggle_variables():
        """Toggles the GUI for namer variables"""
        if namer_gui_variables.showing:
            actions.user.namer_hide_variables()
        else:
            actions.user.namer_show_variables()

    # TODO: Need way to get variables so can filter and search for them
    def namer_get_variable(variable: str):
        """Gets namer variable"""
        return namer_variables[variable]

    def namer_set_variable(variable: str, value: str) -> None:
        """
        Sets namer variable
        """
        # TODO: should namer_variables be sorted for ease of reference?
        namer_variables[variable] = value
        namer_backup_variables()

    def namer_strip_variable(variable: str):
        """Strips namer variable (removes leading / trailing whitespace)"""
        namer_variables[variable] = namer_variables[variable].strip()
        namer_backup_variables()

    def namer_copy_variable(variable: str):
        """Copies current text to clipboard and sets as namer variable"""

        # Workaround, since using actions.edit.copy() seemed to have timing issue (had old clipboard contents stored)
        value = actions.edit.selected_text()
        clip.set_text(value)

        actions.user.namer_clipboard_variable(variable)

    def namer_clipboard_variable(variable: str):
        """Sets namer variable to clipboard contents"""
        value = clip.text()
        actions.user.namer_set_variable(variable, value)

    def namer_clear_variable(variable: str) -> None:
        """
        Clears namer variable (sets to blank)
        """
        namer_variables[variable] = ""
        namer_backup_variables()

    def namer_clear_all_variables() -> None:
        """
        Clears all namer variables (sets to blank)
        """
        for variable in namer_variables.keys():
            namer_variables[variable] = ""

        namer_backup_variables()

    def namer_delete_variable(variable: str) -> None:
        """
        Deletes namer variable
        """
        del namer_variables[variable]
        namer_backup_variables()

    def namer_delete_all_variables() -> None:
        """
        Deletes all namer variables
        """
        namer_variables.clear()
        namer_backup_variables()

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

        logging.debug("namer_make_snippet:")

        snippets_dir = settings.get("user.snippets_dir")
        logging.debug(f"snippets_dir: {snippets_dir}")

        snippet_name = actions.user.reformat_text(name, "camel")
        logging.debug(f"name: {snippet_name}")

        language = actions.code.language()
        logging.debug(f"language: {language}")

        snippet_body = namer_snip_replacement(namer_variables, transformations, body)
        logging.debug(snippet_body)

        user_path = Path(actions.path.talon_user())
        logging.debug(f"user_path: {user_path}")

        if snippets_dir:
            directory = user_path / snippets_dir
        else:
            directory = user_path / "community/core/snippets"

        # TODO: add cleanup to remove invalid characters
        filename = f"{snippet_name}.snippet"
        snippet_path = directory / filename
        logging.debug(f"directory: {directory}")
        logging.debug(f"filename: {filename}")

        snippet = f"""name: {snippet_name}
phrase: {name}
language: {language}
-
{snippet_body}$0
---
"""
        logging.debug("snippet:")
        logging.debug(snippet)

        if not directory.exists():
            logging.error(f"Directory does not exist: {directory}")
            return

        if snippet_path.exists():
            existing_text = snippet_path.read_text()
            stripped_existing_text = existing_text.strip()
            logging.debug("existing text:")
            logging.debug(existing_text)

            if not stripped_existing_text.endswith("---"):
                snippet = "---\n" + snippet

            if not existing_text.endswith("\n"):
                snippet = "\n" + snippet

        with snippet_path.open("a") as myfile:
            myfile.write(snippet)
