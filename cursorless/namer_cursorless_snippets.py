from talon import Module, actions

from ...cursorless_talon.src.targets.target_types import CursorlessTarget

# References:
# * https://discord.com/channels/430796609656193054/430796609656193057/1246884610172915742
# * https://github.com/pokey/pokey_talon/blob/main/apps/vscode/vscode.py

mod = Module()


@mod.action_class
class Actions:
    def insert_snippet_with_cursorless_target(
        name: str, variable_name: str, target: CursorlessTarget
    ):
        """Insert snippet <name> with cursorless target <target>"""
        actions.user.insert_snippet_by_name(
            name,
            {variable_name: actions.user.cursorless_get_text(target)},
        )
