# Referenced: community\plugin\mouse\mouse.py
from talon import Module, actions, cron, ctrl

mod = Module()
mouse_move_job = None
mouse_move_amount_x = 0
mouse_move_amount_y = 0
prior_mouse_x = 0
prior_mouse_y = 0
mouse_move_speed = 1


def mouse_move_continuous_helper():
    global mouse_move_amount_x, mouse_move_amount_y, prior_mouse_x, prior_mouse_y
    x = actions.mouse_x()
    y = actions.mouse_y()
    print(f"x={x}, y={y}; prior_x={prior_mouse_x}, prior_y={prior_mouse_y}")

    if prior_mouse_x != x or prior_mouse_y != y:
        stop_mouse_move()

    # print("scroll_continuous_helper")
    if mouse_move_amount_x or mouse_move_amount_y:
        relative_x = mouse_move_amount_x * mouse_move_speed
        relative_y = mouse_move_amount_y * mouse_move_speed
        actions.user.relative_mouse_move(relative_x, relative_y)
        prior_mouse_x += relative_x
        prior_mouse_y += relative_y


def start_mouse_move():
    global mouse_move_job
    mouse_move_job = cron.interval("60ms", mouse_move_continuous_helper)


def stop_mouse_move():
    global \
        mouse_move_amount_x, \
        mouse_move_amount_y, \
        prior_mouse_x, \
        prior_mouse_y, \
        mouse_move_job
    mouse_move_amount_x = 0
    mouse_move_amount_y = 0
    prior_mouse_x = 0
    prior_mouse_y = 0

    if mouse_move_job:
        cron.cancel(mouse_move_job)

    mouse_move_job = None


@mod.action_class
class Actions:
    def relative_mouse_move(x: int = 0, y: int = 0):
        """Move the cursor to the relative position"""
        if not x and not y:
            return

        ctrl.mouse_move(actions.mouse_x() + x, actions.mouse_y() + y)

    def mouse_move_stop():
        """Stops mouse move"""
        stop_mouse_move()

    def mouse_move_speed(speed: int = 0):
        """Adjust move speed relative to current speed (or 0 to reset)"""
        print("mouse_move_speed:", speed)
        global mouse_move_speed
        if speed == 0:
            mouse_move_speed = 1
            return

        mouse_move_speed += speed
        if mouse_move_speed < 1:
            mouse_move_speed = 1
        elif mouse_move_speed > 10:
            mouse_move_speed = 10

    def mouse_move_continuous(x: int = 0, y: int = 0):
        """Move the cursor continuously"""
        global mouse_move_amount_x, mouse_move_amount_y, prior_mouse_x, prior_mouse_y

        """Moves mouse continuously"""
        if not x and not y:
            return

        actions.user.relative_mouse_move(x, y)
        mouse_move_amount_x = x
        mouse_move_amount_y = y
        prior_mouse_x = actions.mouse_x()
        prior_mouse_y = actions.mouse_y()

        if mouse_move_job is None:
            start_mouse_move()
