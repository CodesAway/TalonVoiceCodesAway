#provide both anchored and unachored commands via 'over'
code <user.text_code_codesaway>$:
    user.add_phrase_to_history(text_code_codesaway)
    insert(text_code_codesaway)
code <user.text_code_codesaway> over:
    user.add_phrase_to_history(text_code_codesaway)
    insert(text_code_codesaway)
