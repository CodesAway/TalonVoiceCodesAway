# Reference community\apps\meld\meld.py
from talon import Context, Module, actions

mod = Module()
ctx = Context()

apps = mod.apps
apps.winmerge = """
os: windows
and app.exe: winmerge.exe
os: windows
and app.exe: winmergeu.exe
"""

ctx.matches = r"""
app: winmerge
"""


@ctx.action_class("app")
class AppActions:
    def tab_open():
        actions.key("ctrl-n")

    def tab_previous():
        actions.key("ctrl-shift-tab")

    def tab_next():
        actions.key("ctrl-tab")

    def tab_reopen():
        print("WinMerge does not support this action.")


@ctx.action_class("user")
class UserActions:
    def tab_jump(number):
        print("WinMerge does not support this action.")

    def tab_final():
        print("WinMerge does not support this action.")

    def tab_duplicate():
        print("WinMerge does not support this action.")
