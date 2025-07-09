mode: user.tag_game
and not mode: sleep
-
^tag stop [<phrase>]$:                          user.tag_game_stop()
^tag hint [<phrase>]$:                          user.tag_game_hint()
^[<phrase>] {user.tag_game_command} [<phrase>]$:
    phrase_1 = phrase_1 or ""
    phrase_2 = phrase_2 or ""
    user.tag_game_handle_command("{phrase_1} {tag_game_command} {phrase_2}")

# Reference community's `talon sleep`
^talon sleep [<phrase>]$:                       speech.disable()

# Reference community's `help alphabet`
help alphabet:                                  user.help_list("user.letter")

# From community (to allow using during game)
help close$:                                    user.help_hide()
