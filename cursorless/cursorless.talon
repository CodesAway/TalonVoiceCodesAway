tag: user.cursorless
-
replace <user.cursorless_target> with <user.cursorless_target>:
    user.cursorless_command("clearAndSetSelection", cursorless_target_1)
    value = user.cursorless_get_text(cursorless_target_2)
    insert(value)

title <user.cursorless_target>:
    value = user.cursorless_get_text(cursorless_target)
    value = user.formatted_text(value, "CAPITALIZE_ALL_WORDS")
    destination = user.cursorless_create_destination(cursorless_target)
    user.cursorless_insert(destination, value)

speak <user.cursorless_target>:
    user.sleep_all()
    user.cursorless_command("setSelection", cursorless_target_1)
    # Plugin: https://marketplace.visualstudio.com/items?itemName=bierner.speech
    user.vscode("speech.speakSelection")
