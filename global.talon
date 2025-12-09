# None is always microphone #1
# (allows turning off mic when watching video to prevent accidental wake up)
# (can click mic icon in Talon HUD to set back to System Default)
mic none please:                                sound.set_microphone("None")
# System Default is always microphone #2
mic default:                                    sound.set_microphone("System Default")

sub show:                                       user.show_subtitles_codesaway()
sub hide:                                       user.hide_subtitles_codesaway()

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

# Tab
[<number_small>] (tabby left | shift tabby):    key("shift-tab:{number_small or 1}")
[<number_small>] tabby [right]:                 key("tab:{number_small or 1}")

<number_small> delete:                          key("backspace:{number_small}")
[<number_small>] deli:                          key("delete:{number_small or 1}")

tab close:                                      user.cmd_ctrl_key("w")
tab (reopen | restore):                         user.cmd_ctrl_key("shift-t")

go back:                                        key("alt-left")
go forward:                                     key("alt-right")

this focus:                                     key("down up")
cancel:                                         key("escape")

boom:                                           insert(", ")

all select:                                     edit.select_all()
this bold:                                      user.cmd_ctrl_key("b")
this copy:                                      edit.copy()
this new:                                       user.cmd_ctrl_key("n")
this open:                                      user.cmd_ctrl_key("o")
this print:                                     user.cmd_ctrl_key("p")
this save:                                      edit.save()
this paste:                                     edit.paste()

# Referenced: community\tags\find\find.talon
hunt <user.text>:                               edit.find(text)

# Referenced: community\tags\find_and_replace\find_and_replace.talon
hunt all <user.text>:
    user.cmd_ctrl_key("shift-f")
    (50ms)
    insert(text)

<user.codesaway_number_prose_prefixed>:         "{codesaway_number_prose_prefixed}"

<user.text_codesaway> flows:
    user.fill_flow(text_codesaway)

selection flows:
    value = edit.selected_text()
    user.fill_flow(value)

dot gov: insert('.gov')

path <user.system_path>: insert('"{system_path}"')

