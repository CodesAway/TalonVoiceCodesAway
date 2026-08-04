from talon import Context, Module

mod = Module()
ctx = Context()

mod.list("notion_language", "The list of languages supported by Notion.")
mod.list("notion_color", "The list of colors supported by Notion.")

apps = mod.apps
apps.notion = """
app: chrome
and title: /notion\\.so/
"""

ctx.matches = r"""
app: notion
"""


@ctx.action_class("user")
class UserActions:
    pass
