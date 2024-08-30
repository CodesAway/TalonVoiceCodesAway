# Referenced: community\plugin\mouse\mouse.py

import logging

from talon import Context, Module, actions, cron, ctrl

mouse_move_speed_default = 5

mod = Module()
mod.tag("mouse_mode", "Allow shorter mouse specific commands")
# https://talon.wiki/Customization/Talon%20Framework/settings

mod.setting(
    "codesaway_mouse_move_speed",
    type=int,
    default=mouse_move_speed_default,
    desc="speed at which to move mouse in continuous mouse move mode",
)

mouse_move_job = None
mouse_move_amount_x = 0
mouse_move_amount_y = 0
prior_mouse_x = 0
prior_mouse_y = 0

# TODO: add setting for mouse_move_continous_default (3) and mouse_move_default (60)
mouse_move_continuous_default = 1
mouse_move_default = 60

auto_mouse_mode = False
user_mouse_mode = False

ctx = Context()


def set_mouse_move_speed(mouse_move_speed: int):
    ctx.settings["user.codesaway_mouse_move_speed"] = mouse_move_speed


def get_mouse_move_speed():
    if "user.codesaway_mouse_move_speed" not in ctx.settings:
        set_mouse_move_speed(mouse_move_speed_default)
        return mouse_move_speed_default

    mouse_move_speed = ctx.settings["user.codesaway_mouse_move_speed"]

    if not mouse_move_speed:
        set_mouse_move_speed(mouse_move_speed_default)
        return mouse_move_speed_default

    return mouse_move_speed


def mouse_move_continuous_helper():
    global mouse_move_amount_x, mouse_move_amount_y, prior_mouse_x, prior_mouse_y
    x = actions.mouse_x()
    y = actions.mouse_y()

    if prior_mouse_x != x or prior_mouse_y != y:
        stop_mouse_move()

    if mouse_move_amount_x or mouse_move_amount_y:
        mouse_move_speed = get_mouse_move_speed()
        relative_x = mouse_move_amount_x * mouse_move_speed
        relative_y = mouse_move_amount_y * mouse_move_speed
        actions.user.relative_mouse_move(relative_x, relative_y)
        prior_mouse_x += relative_x
        prior_mouse_y += relative_y


def start_mouse_move():
    global mouse_move_job, auto_mouse_mode
    mouse_move_job = cron.interval("60ms", mouse_move_continuous_helper)
    auto_mouse_mode = True
    ctx.tags = ["user.mouse_mode"]
    logging.debug("auto_mouse_mode")


def stop_mouse_move():
    global \
        mouse_move_amount_x, \
        mouse_move_amount_y, \
        prior_mouse_x, \
        prior_mouse_y, \
        mouse_move_job, \
        auto_mouse_mode

    auto_mouse_mode = False
    if not user_mouse_mode:
        ctx.tags = []
        logging.debug("done auto_mouse_mode")

    mouse_move_amount_x = 0
    mouse_move_amount_y = 0
    prior_mouse_x = 0
    prior_mouse_y = 0

    if mouse_move_job:
        cron.cancel(mouse_move_job)

    mouse_move_job = None


def direction_as_xy(direction: str, x_amount: int, y_amount: int) -> tuple[int, int]:
    x = 0
    y = 0

    match direction:
        case "1":
            x = -x_amount
            y = y_amount
        case "2":
            y = y_amount
        case "3":
            x = x_amount
            y = y_amount
        case "4":
            x = -x_amount
        case "6":
            x = x_amount
        case "7":
            x = -x_amount
            y = -y_amount
        case "8":
            y = -y_amount
        case "9":
            x = x_amount
            y = -y_amount

    return [x, y]


@mod.action_class
class Actions:
    def set_user_mouse_mode(value: bool):
        """Sets the user mouse mode to the specified value"""
        global user_mouse_mode
        user_mouse_mode = value

        if user_mouse_mode:
            ctx.tags = ["user.mouse_mode"]
            logging.debug("user_mouse_mode")
        elif not auto_mouse_mode:
            ctx.tags = []
            logging.debug("done user_mouse_mode")

    def relative_mouse_move_direction(direction: str, amount: int = 0):
        """Move the cursor to the relative position in the specified direction"""
        if not amount:
            amount = mouse_move_default

        x, y = direction_as_xy(direction, amount, amount)
        actions.user.relative_mouse_move(x, y)

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
        if speed == 0:
            set_mouse_move_speed(mouse_move_speed_default)
            return

        mouse_move_speed = get_mouse_move_speed()

        mouse_move_speed += speed
        if mouse_move_speed < 1:
            mouse_move_speed = 1
        elif mouse_move_speed > 10:
            mouse_move_speed = 10

        set_mouse_move_speed(mouse_move_speed)

    def mouse_move_continuous_direction(direction: str):
        """Move the cursor to the relative position in the specified direction"""
        x, y = direction_as_xy(
            direction, mouse_move_continuous_default, mouse_move_continuous_default
        )
        actions.user.mouse_move_continuous(x, y)

    def mouse_move_continuous(x: int = 0, y: int = 0):
        """Move the cursor continuously"""
        global mouse_move_amount_x, mouse_move_amount_y, prior_mouse_x, prior_mouse_y

        if x == 0 and y == 0:
            return

        if x is None:
            x = 3

        actions.user.relative_mouse_move(x, y)
        mouse_move_amount_x = x
        mouse_move_amount_y = y
        prior_mouse_x = actions.mouse_x()
        prior_mouse_y = actions.mouse_y()

        if mouse_move_job is None:
            start_mouse_move()
