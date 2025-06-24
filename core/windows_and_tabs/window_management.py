import logging
import os
import re
from typing import Tuple

from talon import (
    Context,
    Module,
    actions,
    registry,
    ui,  # type: ignore
)

DROPBOX_PROGRAMS_DIRECTORY = "%UserProfile%/Dropbox/Programs"

mod = Module()

mod.list("open_apps", "Apps which can be openned using {user.open_apps} open")
mod.list("launch_apps_scope", "Launch apps keywords from {user.launch}")

ctx = Context()

# Only include paths which cannot be determined using launch apps
# (for example word and VSCode are handled above, which will find them even if in different location)
ctx.lists["user.open_apps"] = {
    "chrome": "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "winmerge": f"{DROPBOX_PROGRAMS_DIRECTORY}/WinMergePortable/App/WinMerge/WinMergeU.exe",
    "explore": f"{DROPBOX_PROGRAMS_DIRECTORY}/FreeCommanderPortable/FreeCommanderPortable.exe",
    "keepass": f"{DROPBOX_PROGRAMS_DIRECTORY}/KeePass/KeePass.exe",
}

launch_apps_scope = ["obsidian", "task manager", "word", "code", "spotify", "git hub"]
ctx.lists["user.launch_apps_scope"] = launch_apps_scope

# Populated on first run (don't worry about updating for now)
launch_apps: dict[str, str] = {}


@mod.capture(rule="{user.open_apps}")
def open_apps(app) -> str:
    return app.open_apps


@mod.capture(rule="{user.launch_apps_scope}")
def launcher_apps(app) -> tuple[str, str]:
    global launch_apps

    if len(launch_apps) == 0:
        for e in registry.lists["user.launch"][0].items():
            if e[0] in launch_apps_scope:
                launch_apps[e[0]] = e[1]

    # Convert from Capture to string
    app_name = str(app)
    return (app_name, launch_apps[app_name])


@mod.action_class
class Actions:
    # TODO: enhance based on file:///Users/cross/AppData/Roaming/talon/user/community/core/windows_and_tabs/window_snap.py
    def bring_app(path: str) -> None:
        """
        Open application at specified path (replacing environment variables and focusing if already open)
        """
        expand_path = os.path.expandvars(path).lower().replace("/", "\\")
        foreground_apps = ui.apps(background=False)

        for cur_app in foreground_apps:
            if cur_app.exe.lower() == expand_path:
                # logging.debug(f"Focus: {path}")
                cur_app.focus()
                return

        # logging.debug(f"Launch: {path}")
        actions.user.switcher_launch(expand_path)

    # TODO: how to specify that it really is a tuple[str, str]?
    # (for now, this fixes the error at least and the code works as expected)
    def launch_app(app: Tuple[str, ...]) -> None:
        """
        Open application (focusing if already open)
        """
        window = find_window(normalized_executable=app[0])
        if window:
            window.focus()
            return

        actions.user.switcher_launch(app[1])

    def snap_window_to_position_twice(position_name: str) -> None:
        """
        Snap window to position (twice as workaround)
        """
        # Workaround since if in full screen, doesn't snap correctly on first time on Windows 11
        # TODO: look into C:\Users\cross\AppData\Roaming\talon\user\community\core\windows_and_tabs\window_snap.py
        actions.user.snap_window_to_position(position_name)
        actions.user.snap_window_to_position(position_name)

    def maximize_title(title: str) -> None:
        """
        Maximize window with specified title (leave blank to target active window)
        """
        window = hunt_window(title)
        if window:
            window.maximized = True

    def minimize_title(title: str) -> None:
        """
        Minimize window with specified title (leave blank to target active window)
        """
        window = hunt_window(title)
        if window:
            window.minimized = True

    def minimize_all():
        """
        Minimize all windows
        """
        actions.key("win-d")

    def focus_title(title: str) -> None:
        """
        Focus on window with specified title
        """
        window = hunt_window(title)
        if window:
            window.focus()


def normalize_title(title):
    return re.sub("[-_() ]", "", title.lower())


def find_window(normalized_title="", normalized_executable="", ignore_active=False):
    # Reference: https://dragonfly.readthedocs.io/en/latest/_modules/dragonfly/actions/action_focuswindow.html
    windows = ui.windows()
    for window in windows:
        if window.hidden:
            continue

        if normalized_title:
            # Normalize window title to ignore symbols (to allow matching titles based on how would read title)
            normalized_window_title = normalize_title(window.title)
            if normalized_window_title.find(normalized_title) == -1:
                continue

        if normalized_executable:
            normalized_window_executable = normalize_title(
                os.path.basename(window.app.exe)
            )
            if normalized_window_executable.find(normalized_executable) == -1:
                continue

        if ignore_active and window == ui.active_window():
            continue

        # TODO: currently just match first instance (could give score and match best match)
        logging.debug(f"Found ({window.app.exe})! {window.title}")
        return window

    return None


def hunt_window(title):
    if not title:
        return ui.active_window()

    normalized_title = normalize_title(title)
    window = find_window(normalized_title, ignore_active=True)

    # Couldn't find a window, try as executable name
    if not window:
        window = find_window(normalized_executable=normalized_title, ignore_active=True)

    return window


# Implement winwait using user.switcher_focus_app
