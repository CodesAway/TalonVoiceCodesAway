tag: terminal
-

# Note: don't make <user.text> optional, otherwise formatted text doesn't seem to work (only uses first word...)
# Note: don't use <user.text> since formatting text isn't working as expected
change <user.format_text_codesaway>:            user.terminal_change_directory(format_text_codesaway)

linux unregister:
    insert("wsl --unregister Ubuntu")
    key("enter")

linux install:
    insert("wsl --install")
    key("enter")
