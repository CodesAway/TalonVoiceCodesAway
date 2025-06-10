not tag: user.tag_metroid
-
^tag play$:                                     user.tag_game_play()
^tag play <user.tag_game_module>$:              user.tag_game_play(tag_game_module, false)
^tag play alpha <user.tag_game_module>$:        user.tag_game_play(tag_game_module)
