^fisher$:                                       user.fisher_toggle_search_results()
fisher clip:                                    user.fisher_search(clip.text())
fisher hunt <user.text_codesaway>:              user.fisher_draft(text_codesaway)
fisher show:                                    user.fisher_draft("")
fisher hide:                                    user.draft_hide()

fisher submit:
    search_text = user.draft_get_text()
    # TODO: how to replace text with original text (to restore to prior text)
    user.draft_hide()
    user.fisher_search(search_text)

# TODO: support optionally specifying a program to open the file
# (such as if want to open Python files using vscode)
# Could also add FISHer specific defaults, so always opens in VSCode, even though system will open in Python executable
fisher <number_small>:
    user.fisher_hide_search_results()
    pathname = user.fisher_get_search_result_pathname(number_small)
    user.fisher_open_file(pathname)

fisher copy <number_small>:
    pathname = user.fisher_get_search_result_pathname(number_small)
    clip.set_text(pathname)

fisher copy folder <number_small>:
    pathname = user.fisher_get_search_result_pathname(number_small)
    pathname = user.get_directory(pathname)
    clip.set_text(pathname)

fisher index:
    app.notify("FISHer indexing...")
    user.fisher_index_files()

fisher <number_small> {user.fisher_program}:
    user.fisher_hide_search_results()
    pathname = user.fisher_get_search_result_pathname(number_small)
    user.fisher_open_file(pathname, fisher_program)

fisher <number_small> flows:
    user.fisher_hide_search_results()
    pathname = user.fisher_get_search_result_pathname(number_small)
    user.fill_flow(pathname)
