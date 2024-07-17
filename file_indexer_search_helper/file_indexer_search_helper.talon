^fishy$:                                        user.fishy_toggle_search_results()
fishy hunt <user.text_codesaway>:               user.fishy_draft(text_codesaway)

fishy show:                                     user.fishy_draft("")

fishy hide:                                     user.draft_hide()

fishy submit:
    search_text = user.draft_get_text()
    # TODO: how to replace text with original text (to restore to prior text)
    user.draft_hide()
    user.fishy_search(search_text)
