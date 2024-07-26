tag: user.code_operators_assignment
-
assign <user.text_code_codesaway>:
    formatter = user.get_setting("user.code_public_variable_formatter")
    variable = user.formatted_text(text_code_codesaway, formatter)
    result = "{variable} = "
    user.add_phrase_to_history(result)
    key("home")
    insert(result)
