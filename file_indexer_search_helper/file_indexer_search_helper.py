import logging
import os
import os.path
import sqlite3
import subprocess
import sys
from pathlib import Path

from talon import (
    Module,
    actions,
    app,  # type: ignore
    cron,  # type: ignore
    imgui,  # type: ignore
    ui,  # type: ignore
)

from .file_indexer_search_helper_background import (
    TABLE_NAME,
    determine_filename,
    determine_fisher_lock_path,
)

mod = Module()

fisher_subprocess: subprocess.Popen = None
fisher_search_text = ""
fisher_draft_search_text = ""

# Runtime priorities of file extension
# (can be changed on-the-fly without reindex, since passed into SQL query)
# TODO: move to talon_list file
priority_file_extensions = ["exe", "lnk", "md", "talon", "chm"]

# TODO: support deleted directories (should delete from database)
# For example, if doesn't iterate due to ignoring directory

# https://github.com/sqlalchemy/sqlalchemy/discussions/9466#discussioncomment-5273152


# Treat index as priority (so lower index has higher priority)
# If not in list, has lowest priority
# Join string helps make SQL pretty formatted (useful when debugging)
priority_file_extensions_sql = ",\n    ".join(
    [f"('{e}', {i})" for i, e in enumerate(priority_file_extensions)]
)

COUNT_BY_DIRECTORY = f"""
select f.directory, count(1) as count
from {TABLE_NAME} f
group by f.directory
order by count(1) desc
limit 25
"""

COUNT_BY_EXTENSION = f"""
select f.directory, f.extension, count(1) as count
from {TABLE_NAME} f
group by f.directory, f.extension
order by count(1) desc
limit 25
"""


# Note: 'OR' is case-sensitive to match as operator
# PYTHON_JAVA_FULL_TEXT_SEARCH = f"""
# SELECT *
# FROM {TABLE_NAME}('python OR java');
# """


@imgui.open()
def fisher_gui_search_results(gui: imgui.GUI):
    gui.text("Search Results for")
    gui.text(fisher_search_text.replace("\n", " "))
    gui.line()
    search_results = search(fisher_search_text)
    for i, search_result in enumerate(search_results):
        directory = search_result["directory"]
        filename = search_result["filename"]

        gui.text(f"{i+1:02d}: {directory}")
        gui.text(f"{filename}")

        gui.spacer()

    if gui.button("Fisher"):
        actions.user.fisher_hide_search_results()


def handle_stale_fisher_lock() -> bool:
    """
    Handles cases where lock file was left lingering due to issue (and deletes lock file if stale)

    Returns:
        * True if stale lock has been handled (meaning it's okay to start another process)
        * False if the lock remains (meaning another process is still running and a new one should not be started)
    """
    fisher_lock_path = determine_fisher_lock_path(database_pathname)

    if not fisher_lock_path.exists():
        return True

    # Check if PID lock is stale and can be deleted (then, can proceed with indexing)
    with fisher_lock_path.open() as file:
        check_pid = file.read()

    # Store in variable beforehand (to ensure ui.apps doesn't change while iterating)
    ui_apps = ui.apps()
    fisher_python_running = [
        application.name
        for application in ui_apps
        # Match on PID
        if str(application.pid) == check_pid
        # Verify PID is Python process
        and (
            application.name.lower() == "python"
            or os.path.basename(application.exe).lower() == "python.exe"
        )
    ]

    if fisher_python_running:
        return False
    else:
        # PID is stale (since not Python)
        logging.debug("FISHer deleted stale lock")
        fisher_lock_path.unlink()
        return True


def index_files():
    global fisher_subprocess

    if fisher_subprocess:
        fisher_subprocess_is_running = fisher_subprocess.poll() is None
        if fisher_subprocess_is_running:
            # Note: would only get this error if set cron interval too low and prior process didn't finish
            logging.debug(
                "FISHer subprocess is still running (try increasing cron interval)"
            )
            return

    if not handle_stale_fisher_lock():
        logging.debug("FISHer lock remains (don't start another process)")
        return

    file_path = (
        Path(__file__).resolve().with_name("file_indexer_search_helper_background.py")
    )
    fisher_command = [sys.executable, file_path, database_pathname]
    # TODO: add error handling (in case script breaks)
    fisher_subprocess = subprocess.Popen(fisher_command, shell=True)
    logging.debug(
        f"FISHer started background indexing with PID {fisher_subprocess.pid}"
    )


# TODO: show only 10 results and show directory / filename on separate lines with spacer?
# Enable paging (like done for help)
# This may help make results easier to read
def search(FULL_TEXT_SEARCH_TEXT):
    # Note: -e.priority desc will sort NULL / no priority last (since descending)
    # Negative ensures that, for example, priority 0 comes before priority 1
    # (since 0 > -1, so when sorting descending will be earlier)
    FULL_TEXT_SEARCH = f"""
    with extension_xref (extension, priority) as
    (values
        {priority_file_extensions_sql}
    )
    SELECT rowid, e.priority, f.directory, f.name, f.extension, f.size, f.modified_time
    FROM {TABLE_NAME}("{FULL_TEXT_SEARCH_TEXT}") f
    left join extension_xref e on e.extension = f.extension
    order by f.rank, -e.priority desc
    limit 10
    """

    search_results = []

    with sqlite3.connect(database_pathname) as connection:
        cursor = connection.execute(FULL_TEXT_SEARCH)
        for row in cursor:
            row_dict = {cursor.description[i][0]: e for i, e in enumerate(row)}
            row_dict["filename"] = determine_filename(
                row_dict["name"], row_dict["extension"]
            )
            search_results.append(row_dict)

        return search_results

        # print()
        # print("Directories:")
        # for result in connection.execute(COUNT_BY_DIRECTORY).fetchall():
        #     print(result)

        # print()
        # print("Extensions:")
        # for result in connection.execute(COUNT_BY_EXTENSION).fetchall():
        #     print(result)


def on_ready():
    global database_pathname

    # TODO: have user setting
    # (if relative path, make relative to talon user; if absolute, should override, please test)
    database_pathname = os.path.join(
        actions.path.talon_user(), "file_indexer_search_helper.db"
    )

    # TODO: add support for watching directories with recent changes
    # (to allow a dynamic list of instant updates in addition to the 10 minute polling)
    # Would also maintain a list of ignored recent directories (if get permission error)
    # Could have background process write to csv (with directory and modified time)

    cron.after("0s", index_files)

    cron.interval("600s", index_files)

    # search("ada dis*")


app.register("ready", on_ready)


@mod.action_class
class Actions:
    def fisher_hide_search_results():
        """Hides the GUI for fisher search results"""
        fisher_gui_search_results.hide()

    def fisher_show_search_results():
        """Shows the GUI for fisher search results"""
        if fisher_search_text:
            fisher_gui_search_results.show()
        else:
            actions.user.fisher_draft(".she")

    def fisher_toggle_search_results():
        """Toggles the GUI for fisher search results"""
        if fisher_gui_search_results.showing:
            actions.user.fisher_hide_search_results()
        else:
            actions.user.fisher_show_search_results()

    def fisher_draft(search_text: str):
        """Opens draft editor populating with initial search_text (or global fisher_search_text if blank)"""
        actions.user.draft_hide()
        actions.user.draft_show(
            search_text or fisher_draft_search_text or fisher_search_text
        )

    def fisher_search(search_text: str):
        """Search for the specified text"""
        global fisher_search_text
        fisher_search_text = search_text
        actions.user.fisher_show_search_results()
