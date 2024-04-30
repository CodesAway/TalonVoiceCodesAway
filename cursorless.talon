tag: user.cursorless
-
# TODO: implement functionality for transformative templates

store {user.codesaway_template_variables} <user.cursorless_target>:
    value = user.cursorless_get_text(cursorless_target)
    user.store_template_variable(codesaway_template_variables, value)

store <user.text> <user.cursorless_target>:
    value = user.cursorless_get_text(cursorless_target)
    user.store_template_variable(text, value)

# Reference: https://github.com/FireChickenProductivity/Talon-Voice-multidimensional-clipboard/blob/main/cursorless.talon
# copy [that] <user.letter> (target|at) <user.cursorless_target>:
#     text = user.cursorless_get_text(cursorless_target)
#     user.update_multidimensional_clipboard(letter, text)
