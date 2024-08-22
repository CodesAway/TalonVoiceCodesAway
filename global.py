import subprocess

from talon import Context, Module, actions, app, settings
from talon.scripting.types import SettingValue

mod = Module()
mod.list("codesaway_symbol_key", desc="extra symbol keys")

mod.tag(
    "codesaway_subtitles_show",
    "Show custom subtitles using CodesAway settings",
)

ctx = Context()
ctx.lists["user.codesaway_symbol_key"] = {
    "semi": ";",
    "quotes": '"',
    "round": "(",
    "right round": ")",
}


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

    def show_subtitles():
        """Shows subtitles"""
        ctx.tags = ["user.codesaway_subtitles_show"]

    def hide_subtitles():
        """Hides subtitles"""
        ctx.tags = []
