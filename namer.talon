namer:                                          user.toggle_namer_variables()

namer clear {user.namer_variable}:              user.clear_namer_variable(namer_variable)
namer clear all:                                user.clear_all_namer_variables()

namer delete {user.namer_variable}:             user.delete_namer_variable(namer_variable)

namer set {user.namer_variable}:
    value = edit.selected_text()
    user.set_namer_variable(namer_variable, value)

namer create <user.text>:
    value = edit.selected_text()
    user.set_namer_variable(text, value)

namer assign <user.text> with <user.text>:      user.set_namer_variable(text_1, text_2)
