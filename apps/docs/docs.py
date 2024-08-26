from talon import Context, Module, actions

mod = Module()
ctx = Context()

apps = mod.apps
apps.docs = """
app: chrome
and title: /Google Docs/
"""

ctx.matches = r"""
app: docs
"""


@ctx.action_class("user")
class UserActions:
    def select_previous_occurrence(text: str):
        actions.edit.find(text)
        actions.sleep("100ms")
        actions.key("shift-enter esc")

    def select_next_occurrence(text: str):
        actions.edit.find(text)
        actions.sleep("100ms")
        actions.key("esc")
