^namer$:                                        user.toggle_namer_variables()

namer clear <user.text>:                        user.clear_namer_variable(text)
namer clear all:                                user.clear_all_namer_variables()

namer delete <user.text>:                       user.delete_namer_variable(text)

namer set <user.text>:
    value = edit.selected_text()
    user.set_namer_variable(text, value)

# Can be used if <user.text> does not allow saying numbers via "numb 1"
# namer set numb <user.number_string>:
#     value = edit.selected_text()
#     user.set_namer_variable(number_string, value)

namer assign <user.text> with <user.text>:      user.set_namer_variable(text_1, text_2)

namer strip <user.text>:                        user.strip_namer_variable(text)
namer copy <user.text>:                         user.copy_namer_variable(text)
namer clip <user.text>:                         user.clipboard_namer_variable(text)

namer peek <user.text>:
    value = user.get_namer_variable(text)
    insert(value)

# Reference: community\core\snippets\snippets.talon
namer snip {user.snippet}:                      user.namer_insert_snippet(snippet)

namer make snip <user.text>:
    snip = edit.selected_text()
    user.namer_make_snippet(text, snip)
