tag: user.cursorless
-
# TODO: support getting text from list of targets (decide how to combine)
store {user.codesaway_template_variables} <user.cursorless_target>:
    value = user.cursorless_get_text(cursorless_target)
    user.store_template_variable(codesaway_template_variables, value)

store <user.text> <user.cursorless_target>:
    value = user.cursorless_get_text(cursorless_target)
    user.store_template_variable(text, value)

stack <user.cursorless_target>:
    values = user.cursorless_get_text_list(cursorless_target)
    user.push_template_stack_list(values)
    user.cursorless_command("remove", cursorless_target)

push <user.cursorless_target>:
    values = user.cursorless_get_text_list(cursorless_target)
    user.push_template_stack_list(values)

pop <user.cursorless_destination>:
    value = user.pop_template_stack()
    user.cursorless_insert(cursorless_destination, value)

peek <user.cursorless_destination>:
    value = user.peek_template_stack()
    user.cursorless_insert(cursorless_destination, value)
