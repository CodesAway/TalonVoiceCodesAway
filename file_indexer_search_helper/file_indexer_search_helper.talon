^fisher$:                                       user.fisher_toggle_search_results()
fisher hunt <user.text_codesaway>:              user.fisher_draft(text_codesaway)

fisher show:                                    user.fisher_draft("")

fisher hide:                                    user.draft_hide()

fisher submit:
    search_text = user.draft_get_text()
    # TODO: how to replace text with original text (to restore to prior text)
    user.draft_hide()
    user.fisher_search(search_text)
