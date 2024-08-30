mode: user.tag_game
-
^tag stop$:                                     user.tag_game_stop()
^tag hint$:                                     user.tag_game_hint()
^[<phrase>] {user.tag_game_command} [<phrase>]$:
    phrase_1 = phrase_1 or ""
    phrase_2 = phrase_2 or ""
    user.tag_game_handle_command("{phrase_1} {tag_game_command} {phrase_2}")
