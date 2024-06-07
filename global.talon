os: windows
-
settings():
    user.mouse_enable_pop_click = 2
    user.mouse_enable_hiss_scroll = true

# Reference: https://github.com/talonhub/community/blob/main/core/edit/edit.talon
# (has other edit commands)
<number_small> up: key("up:{number_small}")
<number_small> down: key("down:{number_small}")
<number_small> left: key("left:{number_small}")
<number_small> right: key("right:{number_small}")

# Shift + key
<number_small> ups: key("shift-up:{number_small}")
<number_small> downs: key("shift-down:{number_small}")
<number_small> lefts: key("shift-left:{number_small}")
<number_small> rights: key("shift-right:{number_small}")

# Ctrl + key (usually moves cursor)
[<number_small>] word delete: key("ctrl-backspace:{number_small or 1}")
[<number_small>] word deli: key("ctrl-delete:{number_small or 1}")

[<number_small>] graph up: key("ctrl-up:{number_small or 1}")
[<number_small>] graph down: key("ctrl-down:{number_small or 1}")

[<number_small>] word left: key("ctrl-left:{number_small or 1}")
[<number_small>] word right: key("ctrl-right:{number_small or 1}")

# Ctrl + shift + key (usually selects text)
[<number_small>] graph ups: key("ctrl-shift-up:{number_small or 1}")
[<number_small>] graph downs: key("ctrl-shift-down:{number_small or 1}")

[<number_small>] word lefts: key("ctrl-shift-left:{number_small or 1}")
[<number_small>] word rights: key("ctrl-shift-right:{number_small or 1}")

# Tab
[<number_small>] (tabby left | shift tabby): key("shift-tab:{number_small or 1}")
[<number_small>] tabby [right]: key("tab:{number_small or 1}")

<number_small> delete: key("backspace:{number_small}")
[<number_small>] deli: key("delete:{number_small or 1}")

[<number_small>] tab (last | left): key("ctrl-pageup:{number_small or 1}")
# Added "tab wipe" as workaround, since Talon frequently hears "tab wipe" when I say "tab right"
[<number_small>] tab (next | right | wipe): key("ctrl-pagedown:{number_small or 1}")
tab close: key("ctrl-w")
tab (reopen | restore): key("ctrl-shift-t")

go back: key("alt-left")
go forward: key("alt-right")

this focus: key("down up")
cancel: key("escape")

boom: insert(", ")

# PowerToys Run
# (used instead of Fluent Search which TRS didn't allow and got me fired)
# TODO: need to implements
run show: key("alt-space")

# CopyQ ClipsCustom global hotkey
clip show: key("ctrl-alt-shift-f10")

apps: key("menu")

all select: edit.select_all()
this bold: key("ctrl-b")
this copy: edit.copy()
this new: key("ctrl-n")
this open: key("ctrl-o")
this print: key("ctrl-p")
this save: edit.save()
this paste: edit.paste()
[<number_small>] redo: key("ctrl-y:{number_small or 1}")
[<number_small>] undo: key("ctrl-z:{number_small or 1}")
this rename: key("f2")
this refresh: key("f5")

# Referenced: community\tags\find\find.talon
hunt <user.text>$:
    key("ctrl-f")
    sleep(50ms)
    insert(text or "")

# user\community\core\text\formatters.py
# code_formatter_names = {                      # TODO: add Caster version for ones which previously used?
#     "all cap": "ALL_CAPS",                    # yell
#     "all down": "ALL_LOWERCASE",              # laws
#     "camel": "PRIVATE_CAMEL_CASE",
#     "dotted": "DOT_SEPARATED",                # peble
#     "dub string": "DOUBLE_QUOTED_STRING",
#     "dunder": "DOUBLE_UNDERSCORE",
#     "hammer": "PUBLIC_CAMEL_CASE",
#     "kebab": "DASH_SEPARATED",                # spine
#     "packed": "DOUBLE_COLON_SEPARATED",
#     "padded": "SPACE_SURROUNDED_STRING",
#     "slasher": "SLASH_SEPARATED",             # incline
#     "smash": "NO_SPACES",                     # gum / gun
#     "snake": "SNAKE_CASE",
#     "string": "SINGLE_QUOTED_STRING",
# }
# prose_formatter_names = {
#     "say": "NOOP",
#     "speak": "NOOP",
#     "sentence": "CAPITALIZE_FIRST_WORD",      # sing
#     "title": "CAPITALIZE_ALL_WORDS",          # tie
# }

# TODO: convert from Caster to Talon
# Choice(
#     "spacing",
#     {
#         "dissent": 6,  # backslash\words
#         "descent": 6,  # backslash\words
#     },
# ),

# TODO: Convert from Caster to Talon
# (might use existing stuff first and just call it using the commands below)
# # Mouse control (based on Dragon)
# "<mouse_dir> mouse move": R(Function(mouse_move)),
# "<mouse_dir> mouse drag": R(Function(mouse_drag)),
# "mouse focus left": R(
#     Mimic("MouseGrid", "four", "click")
# ),  # Used in training to focus on window (inner content)
# "mouse focus": R(
#     Mimic("MouseGrid", "five", "click")
# ),  # Used in training to focus on window (inner content)
# "mouse focus right": R(
#     Mimic("MouseGrid", "six", "click")
# ),  # Used in training to focus on window (inner content)
