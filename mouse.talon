os: windows
-
mouse stop:                 user.mouse_move_stop()

one mouse move:             user.mouse_move_continuous(-6, 6)

mouse down:                 user.relative_mouse_move(0, 60)
mouse downer | two mouse move: user.mouse_move_continuous(0, 6)

three mouse move:           user.mouse_move_continuous(6, 6)

mouse left:                 user.relative_mouse_move(-60, 0)
mouse lefter | four mouse move: user.mouse_move_continuous(-6, 0)

five mouse move:
    user.mouse_move_stop()
    user.grid_activate()

mouse right:                user.relative_mouse_move(60, 0)
mouse righter | six mouse move: user.mouse_move_continuous(6, 0)

seven mouse move:           user.mouse_move_continuous(-6, -6)

mouse up:                   user.relative_mouse_move(0, -60)
mouse upper | eight mouse move: user.mouse_move_continuous(0, -6)

nine mouse move:            user.mouse_move_continuous(6, -6)

mouse faster:               user.mouse_move_speed(1)
mouse slower:               user.mouse_move_speed(-1)
mouse speed reset:          user.mouse_move_speed(0)

[flex] grid close:
    user.flex_grid_deactivate()
    user.grid_close()

grid off:
    user.flex_grid_deactivate()
    user.grid_close()
