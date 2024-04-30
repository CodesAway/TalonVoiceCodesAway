store show:                 user.show_template_variables_list()
store close:                user.hide_template_variables_list()

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
