import subprocess

from talon import Context, Module, actions, app, settings
from talon.scripting.types import SettingValue

mod = Module()
mod.list("codesaway_symbol_key", desc="extra symbol keys")

ctx = Context()
ctx.lists["user.codesaway_symbol_key"] = {
    "semi": ";",
    "quotes": '"',
    "round": "(",
    "right round": ")",
}

ctx_subtitles = Context()
ctx_subtitles.matches = r"""
mode: all
"""


# Reference: https://old.talon.wiki/unofficial_talon_docs/
@ctx.capture("user.symbol_key", rule="{user.symbol_key} | {user.codesaway_symbol_key}")
def symbol_key(m):
    return str(m)


def on_ready():
    actions.sound.set_microphone("System Default")


app.register("ready", on_ready)


# Reference: https://github.com/AndreasArvidsson/andreas-talon/blob/master/core/operating_system/operating_system.py
child_processes = []


@mod.action_class
class Actions:
    def exec(command: str):
        """Execute command"""
        # Store child process handle to avoid log warning about subprocess still running
        child_processes.append(
            subprocess.Popen(command, shell=True),
        )

    def get_setting(setting_name: str) -> SettingValue:
        """Gets setting with specified name"""
        return settings.get(setting_name)

    def show_subtitles_codesaway():
        """Shows subtitles"""
        # Custom subtitles (added to community on July 7, 2024)
        # https://github.com/talonhub/community/pull/1467
        ctx_subtitles.settings = {
            "user.subtitles_show": True,
            "user.subtitles_timeout_min": 1500,
            "user.subtitles_y": 0.90,
        }

    def hide_subtitles_codesaway():
        """Hides subtitles"""
        ctx_subtitles.settings["user.subtitles_show"] = False
