temp show vars:             user.show_template_variables_list()
temp close:                 user.hide_template_variables_list()

temp clear var {user.codesaway_template_variables}: user.clear_template_variable(codesaway_template_variables)
temp clear all vars:        user.clear_all_template_variables()

temp delete var {user.codesaway_template_variables}: user.delete_template_variable(codesaway_template_variables)

temp var {user.codesaway_template_variables}:
    value = edit.selected_text()
    user.store_template_variable(codesaway_template_variables, value)

temp create var <user.text>:
    value = edit.selected_text()
    user.store_template_variable(text, value)

temp assign var <user.text> is <user.text>: user.store_template_variable(text_1, text_2)
