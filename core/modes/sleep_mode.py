# pokey_talon/core/modes/sleep_mode/sleep_mode.py
from talon import Context, Module, actions

mod = Module()

wake_ctx = Context()


@mod.action_class
class Actions:
    def maybe_hide_history():
        """Hides history if mode wants it"""

    def sleep_all():
        # Reference: community\core\modes\modes_not_dragon.talon
        """Sleeps talon and hides everything"""
        actions.user.switcher_hide_running()
        actions.user.maybe_hide_history()
        actions.user.homophones_hide()
        actions.user.help_hide()
        actions.user.mouse_sleep()
        actions.speech.disable()
        # actions.user.engine_sleep() # Comment out since otherwise disables twice and Talon shows notification

    def wake_all():
        """Wakes talon and shows everything"""
        actions.user.cancel_in_flight_phrase()
        actions.user.mouse_wake()
        actions.user.talon_mode()


@wake_ctx.action_class("user")
class WakeUserActions:
    def maybe_hide_history():
        pass
