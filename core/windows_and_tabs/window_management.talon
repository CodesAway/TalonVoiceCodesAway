<user.open_apps> open:                          user.bring_app(open_apps)
<user.launcher_apps> open:                      user.launch_app(launcher_apps)

# Referenced: user\community\core\windows_and_tabs\window_snap.py
# Noticed that if maximized, needs to be snapped twice to be correct (noticed all windows on Windows 11)
window left:                                    user.snap_window_to_position_twice("LEFT")
window right:                                   user.snap_window_to_position_twice("RIGHT")
# TODO: Noticed maximize doesn't work for VSCode, but other windows no issue (maybe not targetting the right window of the app??)
[window] maximize [<user.text>]:                user.maximize_title(text or "")
[window] minimize [<user.text>]:                user.minimize_title(text or "")
minimize all:                                   user.minimize_all()

# Added since noticed Windows settings window isn't part of user.running_applications (not sure why though...)
focus <user.text>:                              user.focus_title(text)

# # Window
# "window restore": R(Function(restore_window)),
# "app <executable>": R(Function(focus_executable)),
# "focus [on] <title>": R(Function(focus_title)),
# "[window] minimize [<title>]": R(Function(minimize_title)),
# "[window] maximize [<title>]": R(Function(maximize_title)),
