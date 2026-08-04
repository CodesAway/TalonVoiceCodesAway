app: sheets
-

# Workaround to ensure arrow navigation is reliable
settings():
    key_wait = 6.0

# must enable keyboard shortcuts (help menu -> keyboard shortcuts -> enable compatible)

# Focus named ranges box (Ctrl-J)
cell <user.letter> <user.number_prose_unprefixed>:
    key("ctrl-j")
    sleep(100ms)
    insert("{letter}{number_prose_unprefixed}")
    key(enter)

today insert:                                   key("ctrl-;")
