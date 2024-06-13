tag: user.code_functions
-
# Alias for funky from community\lang\tags\functions.talon
^{user.code_function_modifier}* fun <user.text>$:
    user.code_modified_function(code_function_modifier_list or 0, text)
