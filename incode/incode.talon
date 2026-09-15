^incode$:                                       user.incode_toggle_search_results()
incode clip:                                    user.incode_search(clip.text())
incode hunt <user.text_codesaway>:              user.incode_draft(text_codesaway)
incode show:                                    user.incode_draft("")
incode hide:                                    user.draft_hide()

incode submit:
    search_text = user.draft_get_text()
    # TODO: how to replace text with original text (to restore to prior text)
    user.draft_hide()
    user.incode_search(search_text)

incode <number_small>:
    user.incode_hide_search_results()
    result = user.incode_get_search_result(number_small)
    user.incode_open_file(result)

# incode copy <number_small>:
#     pathname = user.incode_get_search_result(number_small)
#     clip.set_text(pathname)

# incode copy folder <number_small>:
#     pathname = user.incode_get_search_result(number_small)
#     pathname = user.get_directory(pathname)
#     clip.set_text(pathname)

# incode index:
#     app.notify("Incode indexing...")
#     user.incode_index_files()

incode <number_small> {user.incode_program}:
    user.incode_hide_search_results()
    result = user.incode_get_search_result(number_small)
    user.incode_open_file(result, incode_program)

# incode <number_small> flows:
#     user.incode_hide_search_results()
#     result = user.incode_get_search_result(number_small)
#     user.fill_flow(result)
