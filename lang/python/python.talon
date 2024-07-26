code.language: python
-
dot <user.text_code_codesaway>:                 insert('.{user.formatted_text(text_code_codesaway, "snake")}')
var <user.text_code_codesaway>:                 insert(user.formatted_text(text_code_codesaway, "snake"))
# Extends what's in functions.talon to allow customize types (basic types in python.py)
type <user.text_code_codesaway>:                insert(user.formatted_text(text_code_codesaway, "hammer"))
no args:                                        insert('()')
return False:                                   "return False"
return True:                                    "return True"
return <user.text_code_codesaway>:              insert('return {user.formatted_text(text_code_codesaway, "snake")}')
global <user.text_code_codesaway>:              insert('global {user.formatted_text(text_code_codesaway, "snake")}')

# Added "state" since without, "dot char at" is seen separately as "dot" and "char at" (versus combined command)
state <user.code_type> <user.letter>:           insert('{code_type} {letter}')
state <user.code_type> <user.text_code_codesaway>: insert('{code_type} {user.formatted_text(text_code_codesaway, "snake")}')

# Couldn't find way to insert "not" for negation
op not:                                         insert('not ')
type int:                                       insert('int')

state pass:                                     "pass"

for <user.text_code_codesaway> in <user.text_code_codesaway>:
    variable = user.formatted_text(text_code_codesaway_1, 'snake')
    iterable = user.formatted_text(text_code_codesaway_2, 'snake')
    insert("for {variable} in {iterable}")

if <user.text_code_codesaway>:
    insert("if {text_code_codesaway}:")

else if <user.text_code_codesaway>:
    insert("elif {text_code_codesaway}:")
