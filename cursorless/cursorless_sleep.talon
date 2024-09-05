tag: user.cursorless
mode: sleep
-
speak <user.cursorless_target>:
    user.cursorless_command("setSelection", cursorless_target_1)
    # Plugin: https://marketplace.visualstudio.com/items?itemName=bierner.speech
    user.vscode("speech.speakSelection")
