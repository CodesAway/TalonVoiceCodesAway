code.language: python
-
dot <user.text>: insert('.{user.reformat_text(text, "snake")}')
var <user.text>: insert(user.reformat_text(text, "snake"))
# Extends what's in functions.talon to allow customize types (basic types in python.py)
type <user.text>: insert(user.reformat_text(text, "hammer"))
no args: insert('()')
return <user.text>: insert('return {user.reformat_text(text, "snake")}')
global <user.text>: insert('global {user.reformat_text(text, "snake")}')

# Added "state" since without, "dot char at" is seen separately as "dot" and "char at" (versus combined command)
state <user.code_type> <user.letter>: insert('{code_type} {letter}')
state <user.code_type> <user.text>: insert('{code_type} {user.reformat_text(text, "snake")}')

# Couldn't find way to insert "not" for negation
op not: insert('not ')
type int: insert('int')
