^namer$:                                        user.namer_toggle_variables()

# Added to help aid finding existing variable (such as homophones)
namer clear {user.namer_variable}:              user.namer_clear_variable(namer_variable)
# Note: namer clear can be used to create new variables with a blank value
namer clear <user.text>:                        user.namer_clear_variable(text)

namer clear all:                                user.namer_clear_all_variables()

namer delete {user.namer_variable}:             user.namer_delete_variable(namer_variable)
namer delete <user.text>:                       user.namer_delete_variable(text)

namer set {user.namer_variable}:
    value = edit.selected_text()
    user.namer_set_variable(namer_variable, value)

namer set <user.text>:
    value = edit.selected_text()
    user.namer_set_variable(text, value)

# Can be used if <user.text> does not allow saying numbers via "numb 1"
# namer set numb <user.number_string>:
#     value = edit.selected_text()
#     user.namer_set_variable(number_string, value)

namer assign {user.namer_variable} with <user.text>: user.namer_set_variable(namer_variable, text)
namer assign <user.text> with <user.text>:      user.namer_set_variable(text_1, text_2)

namer strip {user.namer_variable}:              user.namer_strip_variable(namer_variable)
namer strip <user.text>:                        user.namer_strip_variable(text)

namer copy {user.namer_variable}:               user.namer_copy_variable(namer_variable)
namer copy <user.text>:                         user.namer_copy_variable(text)

namer clip {user.namer_variable}:               user.namer_clipboard_variable(namer_variable)
namer clip <user.text>:                         user.namer_clipboard_variable(text)

namer peek {user.namer_variable}+:
    user.namer_hide_variables()
    value = user.namer_get_variables(namer_variable_list)
    user.paste(value)

# Reference: community\core\snippets\snippets.talon
namer snip {user.snippet}:                      user.namer_insert_snippet(snippet)

namer make <user.text>:
    snip = edit.selected_text()
    user.namer_make_snippet(text, snip)

into namer {user.namer_variable}:
    value = user.fetch_flow()
    user.namer_set_variable(namer_variable, value)

into namer <user.text>:
    value = user.fetch_flow()
    user.namer_set_variable(text, value)

namer {user.namer_variable} flows:
    value = user.namer_get_variable(namer_variable)
    user.fill_flow(value)
