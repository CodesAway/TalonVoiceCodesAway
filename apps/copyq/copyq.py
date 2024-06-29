from talon import Module, actions

mod = Module()


@mod.action_class
class Actions:
    def copyq_choose(index: int):
        """Choose selected clipboard item and paste it"""
        actions.insert(str(index))
        actions.sleep("250ms")
        actions.key("enter")
