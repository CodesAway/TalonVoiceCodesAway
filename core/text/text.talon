#provide both anchored and unachored commands via 'over'
code <user.text_codesaway>$:
    user.add_phrase_to_history(text_codesaway)
    insert(text_codesaway)
code <user.text_codesaway> over:
    user.add_phrase_to_history(text_codesaway)
    insert(text_codesaway)
