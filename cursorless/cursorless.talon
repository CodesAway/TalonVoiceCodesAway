tag: user.cursorless
-
replace <user.cursorless_target> with <user.cursorless_target>:
    user.cursorless_command("clearAndSetSelection", cursorless_target_1)
    value = user.cursorless_get_text(cursorless_target_2)
    insert(value)
