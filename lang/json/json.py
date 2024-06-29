from talon import Context, Module, actions

mod = Module()
ctx = Context()
# code.language: json (not supported in core/modes/language_modes.py)
ctx.matches = r"""
app: vscode
win.title: /\.json -/
"""


@ctx.action_class("user")
class UserActions:
    def code_comment_line_prefix():
        actions.auto_insert("// ")
