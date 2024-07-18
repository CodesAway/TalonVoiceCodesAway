^fisher$:                                       user.fisher_toggle_search_results()

fisher clip:
    search_text = clip.text()
    user.fisher_search(search_text)

# CodesAway* svg voice*

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
    pathname = user.fisher_get_search_result_pathname(number_small)
    user.open_file(pathname)

fisher copy <number_small>:
    pathname = user.fisher_get_search_result_pathname(number_small)
    clip.set_text(pathname)

fisher index:                                   user.fisher_index_files()

fisher <number_small> {user.fisher_program}:
    pathname = user.fisher_get_search_result_pathname(number_small)
    user.open_file_in_program(pathname, fisher_program)
