tag: user.mouse_mode
os: windows
-
stop:                                           user.mouse_move_stop()

<user.number_key> move:                         user.mouse_move_continuous_direction(number_key)

downer:                                         user.mouse_move_continuous_direction("2")
# Two separate commands (so correctly overrides commands in global)
down:                                           user.relative_mouse_move_direction("2")
<number_small> down:                            user.relative_mouse_move_direction("2", number_small)

lefter:                                         user.mouse_move_continuous("4")
# Two separate commands (so correctly overrides commands in global)
left:                                           user.relative_mouse_move_direction("4")
<number_small> left:                            user.relative_mouse_move_direction("4", number_small)

five move:
    user.mouse_move_stop()
    user.flex_grid_activate()

righter:                                        user.mouse_move_continuous_direction("6")
# Two separate commands (so correctly overrides commands in global)
right:                                          user.relative_mouse_move_direction("6")
<number_small> right:                           user.relative_mouse_move_direction("6", number_small)

upper:                                          user.mouse_move_continuous_direction("8")
# Two separate commands (so correctly overrides commands in global)
up:                                             user.relative_mouse_move_direction("8")
<number_small> up:                              user.relative_mouse_move_direction("8", number_small)

faster:                                         user.mouse_move_speed(1)
slower:                                         user.mouse_move_speed(-1)
speed reset:                                    user.mouse_move_speed(0)

zero move:
    user.mouse_move_stop()
    user.flex_grid_deactivate()
    user.grid_close()
