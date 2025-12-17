from talon import Context, Module

mod = Module()
ctx = Context()

apps = mod.apps
apps.gmail = """
app: chrome
and title: /mail\\.google\\.com/
"""

ctx.matches = r"""
app: gmail
"""


@ctx.action_class("user")
class UserActions:
    pass
