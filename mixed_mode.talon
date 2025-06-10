mode: mixed
# Must include these modes too for Talon to use this command over dictation version
mode: dictation
mode: command
-

# Work around since "cap that" will use rule from dictation_mode.talon
# Instead, want to use rule from text.talon
^cap that$:                                     user.formatters_reformat_selection("CAPITALIZE")
