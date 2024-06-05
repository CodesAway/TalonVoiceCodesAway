os: windows
-
# TODO: add setting for mouse_move_continous (3) and mouse_move_default (60)
mouse stop:                 user.mouse_move_stop()

one mouse move:             user.mouse_move_continuous(-3, 3)

mouse downer | two mouse move: user.mouse_move_continuous(0, 3)
[<number_small>] mouse down:
    amount = number_small or 60
    user.relative_mouse_move(0, amount)

three mouse move:           user.mouse_move_continuous(3, 3)

mouse lefter | four mouse move: user.mouse_move_continuous(-3, 0)
[<number_small>] mouse left:
    amount = number_small or 60
    amount = -1 * amount
    user.relative_mouse_move(amount, 0)

five mouse move:
    user.mouse_move_stop()
    user.grid_activate()

mouse righter | six mouse move: user.mouse_move_continuous(3, 0)
[<number_small>] mouse right:
    amount = number_small or 60
    user.relative_mouse_move(amount, 0)

seven mouse move:           user.mouse_move_continuous(-3, -3)

mouse upper | eight mouse move: user.mouse_move_continuous(0, -3)
[<number_small>] mouse up:
    amount = number_small or 60
    amount = -1 * amount
    user.relative_mouse_move(0, amount)

nine mouse move:            user.mouse_move_continuous(3, -3)

mouse faster:               user.mouse_move_speed(1)
mouse slower:               user.mouse_move_speed(-1)
mouse speed reset:          user.mouse_move_speed(0)

[flex] grid close:
    user.flex_grid_deactivate()
    user.grid_close()

grid off:
    user.flex_grid_deactivate()
    user.grid_close()
