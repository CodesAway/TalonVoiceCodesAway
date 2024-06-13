tag: user.cursorless
-
# "shove" is like a forceful "push" (also removes source text)
shove <user.cursorless_target>:
    values = user.cursorless_get_text_list(cursorless_target)
    user.push_skats_stack_list(values)
    user.cursorless_command("remove", cursorless_target)

<user.ordinals> shove <user.cursorless_target>:
    values = user.cursorless_get_text_list(cursorless_target)
    user.push_skats_stack_index_list(ordinals, values)
    user.cursorless_command("remove", cursorless_target)

push <user.cursorless_target>:
    values = user.cursorless_get_text_list(cursorless_target)
    user.push_skats_stack_list(values)

<user.ordinals> push <user.cursorless_target>:
    values = user.cursorless_get_text_list(cursorless_target)
    user.push_skats_stack_index_list(ordinals, values)

pop <user.cursorless_destination>:
    value = user.pop_skats_stack()
    user.cursorless_insert(cursorless_destination, value)

<user.ordinals> pop <user.cursorless_destination>:
    value = user.pop_skats_stack_index(ordinals)
    user.cursorless_insert(cursorless_destination, value)

peek <user.cursorless_destination>:
    value = user.peek_skats_stack()
    user.cursorless_insert(cursorless_destination, value)

<user.ordinals> peek <user.cursorless_destination>:
    value = user.peek_skats_stack_index(ordinals)
    user.cursorless_insert(cursorless_destination, value)

#    replace me please
