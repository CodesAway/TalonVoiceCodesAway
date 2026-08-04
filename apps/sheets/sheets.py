from talon import Context, Module, actions

mod = Module()
ctx = Context()

apps = mod.apps
apps.sheets = """
app: chrome
and title: /docs.google.com/spreadsheets/
"""

ctx.matches = r"""
app: sheets
"""


@ctx.action_class("user")
class UserActions:
    pass
