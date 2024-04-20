code.language: java
-
# TODO: cache list of variables?
# That way return could reference the existing variables (versus trying to create new)
# Similarly, could have separate commands to create a variable versus reference a variable

dot <user.text>:            insert('.{user.reformat_text(text, "camel")}')
var <user.text>:            insert(user.reformat_text(text, "camel"))
# Extends what's in functions.talon to allow customize types (basic types in java.py)
type <user.text>:           insert(user.reformat_text(text, "hammer"))
no args:                    insert('()')
return <user.text>:         insert('return {user.reformat_text(text, "camel")}')
# Added "state" since without, "dot char at" is seen separately as "dot" and "char at" (versus combined command)
state <user.code_type> <user.letter>: insert('{code_type} {letter}')
state <user.code_type> <user.text>: insert('{code_type} {user.reformat_text(text, "camel")}')
# Use defined types (handles HashMap correctly versus Hashmap)
diamond <user.code_type>:   insert('{code_type}<>')
diamond <user.text>:        insert('{user.reformat_text(text, "hammer")}<>')
