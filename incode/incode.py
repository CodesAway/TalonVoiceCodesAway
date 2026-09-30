import datetime
import logging
import os
import os.path
import platform
import subprocess
import sys
from collections import deque
from pathlib import Path
from typing import Any

from talon import (
    Module,
    actions,
    app,  # type: ignore
    cron,  # type: ignore
    fs,
    imgui,  # type: ignore
    registry,
    ui,  # type: ignore
)

from .incode_background import (
    create_path_dictionary,
    determine_incode_lock_path,
    incode_search,
    upsert_records,
)

has_humanfriendly = False
logger = logging.getLogger(__name__)

try:
    import humanfriendly

    has_humanfriendly = True
except ModuleNotFoundError:
    # Error handling
    logger.info(
        "Dependency humanfriendly isn't available (using default date / time format)"
    )


mod = Module()
mod.list(
    "incode_program",
    "Program name and pathname to open files using Incode",
)
mod.list(
    "incode_file_extension",
    "Map from file extension to user.incode_programs key",
)

incode_subprocess: subprocess.Popen | None = None
incode_search_text = ""
incode_draft_search_text = ""
incode_search_results: list[dict[str, str]] = []


# Note: 'OR' is case-sensitive to match as operator
# PYTHON_JAVA_FULL_TEXT_SEARCH = f"""
# SELECT *
# FROM {TABLE_NAME}('python OR java');
# """

SIZE_PREFIXES = ["", "k", "M", "G", "T", "P", "E", "Z", "Y", "R", "Q"]


def format_size(size: int) -> str:
    index = 0
    formatted_size: float = size
    while formatted_size >= 1000 and index + 1 < len(SIZE_PREFIXES):
        formatted_size /= 1000
        index += 1

    return f"{round(formatted_size, 2)} {SIZE_PREFIXES[index]}B"


def format_datetime(seconds: float) -> str:
    if has_humanfriendly:
        now = datetime.datetime.now().timestamp()
        diff = now - seconds
        if diff < 60:
            return "seconds ago"

        return f"{humanfriendly.format_timespan(now - seconds, max_units=1)} ago"  # type: ignore

    seconds_datetime = datetime.datetime.fromtimestamp(seconds)

    # If doesn't have time part, just show date (noticed lost of old files from Dropbox like this)
    if (
        seconds_datetime.hour
        == seconds_datetime.minute
        == seconds_datetime.second
        == seconds_datetime.microsecond
        == 0
    ):
        return seconds_datetime.strftime("%Y-%m-%d")

    return seconds_datetime.strftime("%Y-%m-%d %H:%M:%S")


@imgui.open()
def incode_gui_search_results(gui: imgui.GUI):
    global incode_search_results
    gui.text("Search Results for")
    gui.text(incode_search_text.replace("\n", " "))
    gui.line()

    max_line_length = 150

    for i, search_result in enumerate(incode_search_results):
        directory = search_result["directory"]
        filename = search_result["name"]

        # Workaround since doesn't use monospace font (so columns don't align)
        gui.text(f"{i + 1:<9d}{Path(directory) / filename}")
        line_number = f"({search_result['line_number']})"
        line_content = search_result["line_content"]

        # Append "..." only if the string exceeds the maximum length
        truncated_text = (
            line_content[:max_line_length] + "..."
            if len(line_content) > max_line_length
            else line_content
        )

        gui.text(f"{line_number:<7}{truncated_text}")

        gui.line()

    if gui.button("Incode"):
        actions.user.incode_hide_search_results()


def handle_stale_incode_lock() -> bool:
    """
    Handles cases where lock file was left lingering due to issue (and deletes lock file if stale)

    Returns:
        * True if stale lock has been handled (meaning it's okay to start another process)
        * False if the lock remains (meaning another process is still running and a new one should not be started)
    """
    incode_lock_path = determine_incode_lock_path(database_path)

    if not incode_lock_path.exists():
        return True

    # Check if PID lock is stale and can be deleted (then, can proceed with indexing)
    with incode_lock_path.open() as file:
        check_pid = file.read()

    # Store in variable beforehand (to ensure ui.apps doesn't change while iterating)
    ui_apps = ui.apps()
    incode_python_running = [
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

    if incode_python_running:
        return False
    else:
        # PID is stale (since not Python)
        logger.debug("Incode deleted stale lock")
        incode_lock_path.unlink()
        return True


def index_files():
    global incode_subprocess

    if incode_subprocess:
        incode_subprocess_is_running = incode_subprocess.poll() is None
        if incode_subprocess_is_running:
            # Note: would only get this error if set cron interval too low and prior process didn't finish
            logger.debug(
                "Incode subprocess is still running (try increasing cron interval)"
            )
            return

    if not handle_stale_incode_lock():
        logger.debug("Incode lock remains (don't start another process)")
        return

    file_path = Path(__file__).resolve().with_name("incode_background.py")

    python_executable = Path(sys.executable)
    while not python_executable.exists():
        python_executable = python_executable.parent
        try_python_executable = python_executable.with_name(
            python_executable.name + ".exe"
        )
        if not python_executable.exists() and try_python_executable.exists():
            python_executable = try_python_executable

    incode_command = [
        python_executable,
        file_path,
        database_path,
        # Directories to index (can be multiple)
        actions.path.talon_user(),
    ]
    print(f"Incode command: {incode_command}")

    # TODO: add error handling (in case script breaks)
    incode_subprocess = subprocess.Popen(incode_command, shell=True)
    logger.debug(f"Incode started background indexing with PID {incode_subprocess.pid}")


def on_ready():
    global database_path

    # TODO: have user setting
    # (if relative path, make relative to talon user; if absolute, should override, please test)
    # TODO: should the DB and log be in the same directory? (maybe talon_home would be a better location)
    database_path = Path(actions.path.talon_home()) / "incode.db"

    # Ignore files related to Incode (since otherwise would get stuck in cycle of handling modified files)
    # ignore_incode_paths = (
    #     database_path,
    #     # TODO: is there a better way to write this?
    #     Path(str(database_path) + "-journal"),
    #     determine_incode_lock_path(database_path),
    #     Path(__file__).resolve().parent / "incode.log",
    # )
    # logger.info(f"Incode Ignore: {ignore_incode_paths}")

    # TODO: add support for watching directories with recent changes
    # (to allow a dynamic list of instant updates in addition to the 10 minute polling)
    # Would also maintain a list of ignored recent directories (if get permission error)
    # Could have background process write to csv (with directory and modified time)

    cron.after("0s", index_files)

    fs.watch(actions.path.talon_user(), on_watch)
    fs.watch(r"C:\Users\cross\Dropbox\Documents\My Documents\Python Random", on_watch)
    # fs.watch("C:\\Users\\cross\\Dropbox\\Documents", on_watch)

    # search("ada dis*")


modified_files: deque[Path] = deque()
modified_files_job = None


def on_watch(path, flags):
    global modified_files_job
    # Use resolve to get the correct casing from file system (prevents duplicates in database on Windows)
    path = Path(path).resolve()

    # print(f"{path} ({flags})")
    # if path in ignore_incode_paths:
    #     return

    # if True:
    #     return

    modified_files.append(path)

    # Handle modified files in batch group
    if modified_files_job:
        cron.cancel(modified_files_job)

    # Wait 2 seconds to see if other files are modified (such as during a code checkout / update)
    # (no longer need to wait after performance changes)
    # modified_files_job = cron.after("2000ms", process_modified_files)
    modified_files_job = cron.after("0ms", process_modified_files)


def process_modified_files():
    global modified_files_job
    # TODO: how to handle if Incode is already locked (doing batch run)
    # (should it just wait 2 seconds and try again?)
    modified_files_job = None
    # TODO: if `file` table doesn't exist, cannot do (such as if modify file before database is created)
    process_modified_files = deque(modified_files)
    # Remove files, since will be already processed
    # Pop from left since these were added first
    # Don't use clear, since more modified files may be added as we're processing, so don't want to clear these
    for _ in range(len(process_modified_files)):
        modified_files.popleft()

    # Handle duplicates
    process_modified_files = set(process_modified_files)

    # logger.debug("Incode process modified files:")
    # TODO: You get notified when files are deleted as well!
    # This allows full processing (if file doesn't exist, delete from index)
    upsert_files: list[dict[str, Any]] = []

    for path in process_modified_files:
        # logger.debug(path)
        try:
            upsert_files.append(create_path_dictionary(path))
        except OSError as e:
            logger.error(f"An error occurred: {e}")

    # TODO: limit to 1000 records at a time to reduce wait time when querying (since locks database on writes)
    upsert_records(database_path, upsert_files)


app.register("ready", on_ready)


@mod.action_class
class Actions:
    def incode_hide_search_results():
        """Hides the GUI for incode search results"""
        incode_gui_search_results.hide()

    def incode_show_search_results():
        """Shows the GUI for incode search results"""
        global incode_search_results
        if incode_search_text:
            search_results = incode_search(database_path, incode_search_text)
            incode_search_results = search_results
            incode_gui_search_results.show()
        else:
            actions.user.incode_draft("")

    def incode_toggle_search_results():
        """Toggles the GUI for incode search results"""
        if incode_gui_search_results.showing:
            actions.user.incode_hide_search_results()
        else:
            actions.user.incode_show_search_results()

    def incode_draft(search_text: str):
        """Opens draft editor populating with initial search_text (or global incode_search_text if blank)"""
        actions.user.draft_hide()
        actions.user.draft_show(
            search_text or incode_draft_search_text or incode_search_text
        )

    def incode_search(search_text: str):
        """Search for the specified text"""
        global incode_search_text
        incode_search_text = search_text
        actions.user.incode_show_search_results()

    def incode_get_search_result(index: int) -> tuple[str, str]:
        """Gets the search results at the specified index"""
        if not incode_search_results:
            logger.debug("Incode has no search results")
            return ("", "0")

        # Subtract 1 to convert from 1-based to 0-based index
        incode_search_result = incode_search_results[index - 1]
        return os.path.join(
            incode_search_result["directory"],
            incode_search_result["name"],
        ), incode_search_result["line_number"]

    def open_file_default_program(pathname: str):
        """Open file in default program"""

        if platform.system() == "Darwin":  # macOS
            subprocess.call(("open", pathname))
        elif platform.system() == "Windows":  # Windows
            os.startfile(pathname)
        else:  # linux variants
            subprocess.call(("xdg-open", pathname))

    def incode_open_file(result: tuple[str, str | int], program_pathname: str = ""):
        """Opens the file"""
        # https://stackoverflow.com/a/435669
        # https://github.com/chaosparrot/talon_hud/blob/908ec641514075326fe2c51db329607ae0b2115c/content/speech_poller.py#L88-L93

        pathname = result[0]
        line_number = result[1]

        if program_pathname == "default":
            actions.user.open_file_default_program(pathname)
            return

        if program_pathname:
            command = [program_pathname, pathname]
            actions.user.exec(command)
            return

        extension = os.path.splitext(pathname)[1]
        if extension:
            # Check if should open this in specific program
            incode_program = registry.lists["user.incode_file_extension"][0].get(
                extension[1:]
            )
            if incode_program:
                program_pathname = registry.lists["user.incode_program"][0].get(
                    incode_program
                )
                if not program_pathname:
                    logger.error(
                        f"Could not find program named '{incode_program}' in user.incode_programs"
                    )
                    return

                program_pathname = os.path.expandvars(program_pathname)

                # TODO: only works for VSCode
                command = [program_pathname, "-r", "-g", f"{pathname}:{line_number}"]
                actions.user.exec(command)
                return

        actions.user.open_file_default_program(pathname)

    def incode_index_files():
        """Index files (ad-hoc)"""
        index_files()
