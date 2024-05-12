store show:                 user.show_template_variables_list()
store close:                user.hide_template_variables_list()
skats:                      user.toggle_template_stack()

store clear {user.codesaway_template_variables}: user.clear_template_variable(codesaway_template_variables)
store clear all:            user.clear_all_template_variables()

store delete {user.codesaway_template_variables}: user.delete_template_variable(codesaway_template_variables)

store {user.codesaway_template_variables}:
    value = edit.selected_text()
    user.store_template_variable(codesaway_template_variables, value)

store create <user.text>:
    value = edit.selected_text()
    user.store_template_variable(text, value)

store assign <user.text> is <user.text>: user.store_template_variable(text_1, text_2)

stack clear:                user.clear_template_stack()

stack delete <number>:      user.delete_template_stack_index(number)

# Insert at cursor cursor position - "pop to this" would replace current
pop here:
    value = user.pop_template_stack()
    insert(value)

<user.ordinals_small> pop here:
    value = user.pop_template_stack_index(ordinals_small)
    insert(value)

peek here:
    value = user.peek_template_stack()
    insert(value)

<user.ordinals_small> peek here:
    value = user.peek_template_stack_index(ordinals_small)
    insert(value)
