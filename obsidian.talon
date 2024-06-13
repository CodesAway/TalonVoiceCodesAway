app: obsidian
-
jump link: key("ctrl-alt-'")
# Lightspeed Jump
jump <user.any_alphanumeric_key> <user.any_alphanumeric_key>: key("ctrl-alt-` {any_alphanumeric_key_1} {any_alphanumeric_key_2}")
jumpy: key("ctrl-alt-;")

bar left: key("alt-l")
bar right: key("alt-r")

open <user.text>:
    key(ctrl-o)
    sleep(50ms)
    insert("{text}")
