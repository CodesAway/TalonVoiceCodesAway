os: windows
-
# Reference: https://github.com/AndreasArvidsson/andreas-talon/blob/master/core/operating_system/operating_system.talon
^system shutdown$:                              user.exec("shutdown /s")
^system restart$:                               user.exec("shutdown /r")
^system lock$:
    user.sleep_all()
    user.exec("Rundll32.exe user32.dll,LockWorkStation")

# Reference: https://github.com/talonhub/community/blob/main/core/edit/edit.talon
# (has other edit commands)
<number_small> up:                              key("up:{number_small}")
<number_small> down:                            key("down:{number_small}")
<number_small> left:                            key("left:{number_small}")
<number_small> right:                           key("right:{number_small}")

# Shift + key
<number_small> ups:                             key("shift-up:{number_small}")
<number_small> downs:                           key("shift-down:{number_small}")
<number_small> lefts:                           key("shift-left:{number_small}")
<number_small> rights:                          key("shift-right:{number_small}")

# Ctrl + key (usually moves cursor)
[<number_small>] word delete:                   key("ctrl-backspace:{number_small or 1}")
[<number_small>] word deli:                     key("ctrl-delete:{number_small or 1}")

[<number_small>] graph up:                      key("ctrl-up:{number_small or 1}")
[<number_small>] graph down:                    key("ctrl-down:{number_small or 1}")

[<number_small>] word left:                     key("ctrl-left:{number_small or 1}")
[<number_small>] word right:                    key("ctrl-right:{number_small or 1}")

# Ctrl + shift + key (usually selects text)
[<number_small>] graph ups:                     key("ctrl-shift-up:{number_small or 1}")
[<number_small>] graph downs:                   key("ctrl-shift-down:{number_small or 1}")

[<number_small>] word lefts:                    key("ctrl-shift-left:{number_small or 1}")
[<number_small>] word rights:                   key("ctrl-shift-right:{number_small or 1}")

# Tab
[<number_small>] (tabby left | shift tabby):    key("shift-tab:{number_small or 1}")
[<number_small>] tabby [right]:                 key("tab:{number_small or 1}")

<number_small> delete:                          key("backspace:{number_small}")
[<number_small>] deli:                          key("delete:{number_small or 1}")

[<number_small>] tab (last | left):             key("ctrl-pageup:{number_small or 1}")
# Added "tab wipe" as workaround, since Talon frequently hears "tab wipe" when I say "tab right"
[<number_small>] tab (next | right | wipe):     key("ctrl-pagedown:{number_small or 1}")
tab close:                                      key("ctrl-w")
tab (reopen | restore):                         key("ctrl-shift-t")

go back:                                        key("alt-left")
go forward:                                     key("alt-right")

this focus:                                     key("down up")
cancel:                                         key("escape")

boom:                                           insert(", ")

# PowerToys Run
# (used instead of Fluent Search which TRS didn't allow and got me fired)
# TODO: need to implements
# run show:                                       key("alt-space")

# CopyQ Custom global hotkey
# clip show:                                      key("ctrl-alt-shift-f10")

apps:                                           key("menu")

all select:                                     edit.select_all()
this bold:                                      key("ctrl-b")
this copy:                                      edit.copy()
this new:                                       key("ctrl-n")
this open:                                      key("ctrl-o")
this print:                                     key("ctrl-p")
this save:                                      edit.save()
this paste:                                     edit.paste()
[<number_small>] redo:                          key("ctrl-y:{number_small or 1}")
[<number_small>] undo:                          key("ctrl-z:{number_small or 1}")
this rename:                                    key("f2")
this refresh:                                   key("f5")

# Referenced: community\tags\find\find.talon
hunt <user.text>$:
    key("ctrl-f")
    sleep(50ms)
    insert(text or "")
