tag: user.cursorless
-
# TODO: support getting text from list of targets (decide how to combine)
namer set {user.namer_variable} <user.cursorless_target>:
    value = user.cursorless_get_text(cursorless_target)
    user.set_namer_variable(namer_variable, value)

namer create <user.text> <user.cursorless_target>:
    value = user.cursorless_get_text(cursorless_target)
    user.set_namer_variable(text, value)

# TODO: Does not validate number already exists (should I add this?)
namer set numb <user.number_string> <user.cursorless_target>:
    value = user.cursorless_get_text(cursorless_target)
    user.set_namer_variable(number_string, value)

namer create numb <user.number_string> <user.cursorless_target>:
    value = user.cursorless_get_text(cursorless_target)
    user.set_namer_variable(number_string, value)
