tag: browser
and not tag: user.rango_disabled
-
# Alias for "button", since can find text as well
seek <user.text>:                               user.rango_run_action_on_text_matched_element("clickElement", text, false)
rango (toggle | switch):                        user.rango_toggle_hints()
