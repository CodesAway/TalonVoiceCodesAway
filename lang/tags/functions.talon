tag: user.code_functions
-
# Alias for funky from community\lang\tags\functions.talon
^{user.code_function_modifier}* funner <user.text>$:
    user.code_modified_function(code_function_modifier_list or 0, text)

# Alias for funk from community\lang\tags\functions_common.talon
fun <user.code_common_function>:                user.code_insert_function(code_common_function, "")

fun <user.text>:
    user.code_public_function_formatter(text)
    insert("()")
    edit.left()
