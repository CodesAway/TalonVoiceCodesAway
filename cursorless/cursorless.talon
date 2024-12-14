tag: user.cursorless
-
replace <user.cursorless_target> with <user.cursorless_target>:
    destination = user.cursorless_create_destination(cursorless_target_1)
    value = user.cursorless_get_text(cursorless_target_2)
    user.cursorless_insert(destination, value)

replace <user.cursorless_target> with <user.text_code_codesaway>:
    destination = user.cursorless_create_destination(cursorless_target)
    user.cursorless_insert(destination, text_code_codesaway)

title <user.cursorless_target>:
    value = user.cursorless_get_text(cursorless_target)
    value = user.formatted_text(value, "CAPITALIZE_ALL_WORDS")
    destination = user.cursorless_create_destination(cursorless_target)
    user.cursorless_insert(destination, value)

speak <user.cursorless_target>:
    user.sleep_all()
    user.cursorless_command("setSelection", cursorless_target)
    # Plugin: https://marketplace.visualstudio.com/items?itemName=bierner.speech
    user.vscode("speech.speakSelection")

# https://github.com/cursorless-dev/cursorless/pull/1821
# info <user.cursorless_target>:
#     target_info = user.private
#     print(target_info)

curse get:                                      user.get_vscode_cursor_position()

# curse get <user.cursorless_target>:             user.get_cursorless_position(cursorless_target)

# Partial Diff Extension
diff <user.cursorless_target>:
    user.cursorless_command("setSelection", cursorless_target)
    user.vscode("extension.partialDiff.markSection1")

diff with <user.cursorless_target>:
    user.cursorless_command("setSelection", cursorless_target)
    user.vscode("extension.partialDiff.markSection2AndTakeDiff")
