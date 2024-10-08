tag: user.cursorless
-
# TODO: support getting text from list of targets (decide how to combine)

namer set {user.namer_variable} [with] <user.cursorless_target>:
    value = user.cursorless_get_text(cursorless_target)
    user.namer_set_variable(namer_variable, value)

namer set <user.text> [with] <user.cursorless_target>:
    value = user.cursorless_get_text(cursorless_target)
    user.namer_set_variable(text, value)

# Can be used if <user.text> does not allow saying numbers via "numb 1"
# namer set numb <user.number_string> <user.cursorless_target>:
#     value = user.cursorless_get_text(cursorless_target)
#     user.namer_set_variable(number_string, value)

namer copy {user.namer_variable} [with] <user.cursorless_target>:
    value = user.cursorless_get_text(cursorless_target)
    clip.set_text(value)
    user.namer_set_variable(namer_variable, value)

namer copy <user.text> [with] <user.cursorless_target>:
    value = user.cursorless_get_text(cursorless_target)
    clip.set_text(value)
    user.namer_set_variable(text, value)

namer make <user.text> [with] <user.cursorless_target>:
    snip = user.cursorless_get_text(cursorless_target)
    user.namer_make_snippet(text, snip)

# TODO: add other cursorless stuff
namer peek {user.namer_variable} <user.cursorless_destination>:
    value = user.namer_get_variable(namer_variable)
    user.cursorless_insert(cursorless_destination, value)
