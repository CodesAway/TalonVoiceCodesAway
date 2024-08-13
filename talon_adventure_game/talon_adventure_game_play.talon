tag: user.tag_game
# Intentionally added to help ensure commands take priority (so don't run command for real)
mode: command
-
^tag stop$:                                     user.tag_game_stop()
{user.tag_game_command}:                        user.tag_game_handle_command(tag_game_command)

# Handle commands specially when required (couldn't figure out how to otherwise match)
# (seems necessary if original command uses "|" to allow alternations)
hunt this (pace | paste):                       user.tag_game_handle_command("hunt this paste")
hunt all (pace | paste):                        user.tag_game_handle_command("hunt all paste")
