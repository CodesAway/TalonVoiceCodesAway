os: windows
-
# Reference: https://github.com/AndreasArvidsson/andreas-talon/blob/master/core/operating_system/operating_system.talon
^system shutdown please$:                       user.exec("shutdown /s")
^system restart please$:                        user.exec("shutdown /r")
^system lock$:
    user.sleep_all()
    user.exec("Rundll32.exe user32.dll,LockWorkStation")

key(ctrl-alt-space):                            user.hud_toggle_microphone()
key(ctrl-shift-space):                          user.screenshot()

# Ctrl + key (usually moves cursor)
[<number_small>] word delete:                   key("ctrl-backspace:{number_small or 1}")
[<number_small>] word deli:                     key("ctrl-delete:{number_small or 1}")

[<number_small>] graph up:                      key("ctrl-up:{number_small or 1}")
[<number_small>] graph down:                    key("ctrl-down:{number_small or 1}")

[<number_small>] word left:                     key("ctrl-left:{number_small or 1}")
[<number_small>] word right:                    key("ctrl-right:{number_small or 1}")

[<number_small>] select word left:              key("ctrl-shift-left:{number_small or 1}")
[<number_small>] select word right:             key("ctrl-shift-right:{number_small or 1}")

# Ctrl + shift + key (usually selects text)
[<number_small>] graph ups:                     key("ctrl-shift-up:{number_small or 1}")
[<number_small>] graph downs:                   key("ctrl-shift-down:{number_small or 1}")

[<number_small>] word lefts:                    key("ctrl-shift-left:{number_small or 1}")
[<number_small>] word rights:                   key("ctrl-shift-right:{number_small or 1}")

# Tab switching
[<number_small>] tab (last | left):             key("ctrl-pageup:{number_small or 1}")
[<number_small>] tab (next | right):            key("ctrl-pagedown:{number_small or 1}")

apps:                                           key("menu")

[<number_small>] redo:                          key("ctrl-y:{number_small or 1}")
[<number_small>] undo:                          key("ctrl-z:{number_small or 1}")

this rename:                                    key("f2")
this refresh:                                   key("f5")

super hunt <user.text>:
    key("super")
    sleep(500ms)
    insert(text)

(go | open) <user.system_path>:
    # args = ["explorer", system_path]
    # print(args)
    # user.run(args)
    user.run2("explorer", system_path)
