# Reference file://c:/Users/cross/AppData/Roaming/talon/user/community/settings.talon
# Don't want to have numbers enter as text, since I use them in my voice grammar
#Related to contents of %AppData%\talon\user\community\core\numbers\numbers_unprefixed.talon
tag(): user.prefixed_numbers
tag(): user.cursorless_use_community_snippets

settings():
    user.mouse_enable_pop_click = 2
    user.snippets_dir = "TalonVoiceCodesAway/snippets"
    # user.mouse_enable_hiss_scroll = true
    # Try longer timeout (default 0.3, so I have more time to pause and think)
    speech.timeout = 0.4
    imgui.dark_mode = true
    # Used by andreas_talon/analyze_phrase/busage.py
    # user.pretty_print_phrase = true
    user.ocr_dark_background_debug_color = "ff00ff"
