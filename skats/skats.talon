^skats$:                                        user.toggle_skats_stack()
stack clear:                                    user.clear_skats_stack()

# Use ordinals for consistency
stack <user.ordinals> delete:                   user.delete_skats_stack_index(ordinals)

# Workaround since cannot seem to say "zeroth" so it will recognize me
stack top delete:                               user.delete_skats_stack_index(0)

stack clip:
    value = clip.text()
    user.push_skats_stack(value)

# Insert at cursor cursor position - "pop to this" would replace current
pop here:
    value = user.pop_skats_stack()
    insert(value)

<user.ordinals> pop here:
    value = user.pop_skats_stack_index(ordinals)
    insert(value)

peek here:
    value = user.peek_skats_stack()
    insert(value)

<user.ordinals> peek here:
    value = user.peek_skats_stack_index()
    insert(value)

push it:
    value = edit.selected_text()
    user.push_skats_stack(value)

swap stack:                                     user.dig_skats_stack(1)
<user.ordinals> dig:                            user.dig_skats_stack(ordinals)
