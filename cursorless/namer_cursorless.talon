tag: user.cursorless
-
# TODO: support getting text from list of targets (decide how to combine)
namer set <user.text> <user.cursorless_target>:
    value = user.cursorless_get_text(cursorless_target)
    user.set_namer_variable(text, value)

# Can be used if <user.text> does not allow saying numbers via "numb 1"
# namer set numb <user.number_string> <user.cursorless_target>:
#     value = user.cursorless_get_text(cursorless_target)
#     user.set_namer_variable(number_string, value)

namer copy <user.text> <user.cursorless_target>:
    value = user.cursorless_get_text(cursorless_target)
    clip.set_text(value)
    user.set_namer_variable(text, value)
