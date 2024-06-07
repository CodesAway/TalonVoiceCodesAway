os: windows
-
^mouse mode$: user.set_user_mouse_mode(true)
^mouse mode off$: user.set_user_mouse_mode(false)

mouse stop: user.mouse_move_stop()

<user.number_key> mouse move: user.mouse_move_continuous_direction(number_key)

mouse downer: user.mouse_move_continuous_direction("2")
[<number_small>] mouse down: user.relative_mouse_move_direction("2", number_small or 0)

# parrot(tut):                user.relative_mouse_move(-10, 0)
# parrot(shush):              user.relative_mouse_move(-10, 0)
# parrot(ah):                 user.relative_mouse_move(-10, 0)
mouse lefter: user.mouse_move_continuous_direction("4")
[<number_small>] mouse left: user.relative_mouse_move_direction("4", number_small or 0)

five mouse move:
    user.mouse_move_stop()
    user.flex_grid_activate()

# parrot(ee):                 user.relative_mouse_move(10, 0)
mouse righter: user.mouse_move_continuous_direction("6")
[<number_small>] mouse right: user.relative_mouse_move_direction("6", number_small or 0)

mouse upper: user.mouse_move_continuous_direction("8")
[<number_small>] mouse up: user.relative_mouse_move_direction("8", number_small or 0)

mouse faster: user.mouse_move_speed(1)
mouse slower: user.mouse_move_speed(-1)
mouse speed reset: user.mouse_move_speed(0)

[flex] grid close:
    user.flex_grid_deactivate()
    user.grid_close()

grid off:
    user.flex_grid_deactivate()
    user.grid_close()

zero mouse move:
    user.mouse_move_stop()
    user.flex_grid_deactivate()
    user.grid_close()
