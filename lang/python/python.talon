code.language: python
-
dot <user.text_code_codesaway>:                 insert('.{user.formatted_text(text_code_codesaway, "SNAKE_CASE")}')
var <user.text_code_codesaway>:                 insert(user.formatted_text(text_code_codesaway, "SNAKE_CASE"))
# Extends what's in functions.talon to allow customize types (basic types in python.py)
type <user.text_code_codesaway>:                insert(user.formatted_text(text_code_codesaway, "PUBLIC_CAMEL_CASE"))
no args:                                        insert('()')
return False:                                   "return False"
return True:                                    "return True"
return <user.text_code_codesaway>:              insert('return {user.formatted_text(text_code_codesaway, "SNAKE_CASE")}')
global <user.text_code_codesaway>:              insert('global {user.formatted_text(text_code_codesaway, "SNAKE_CASE")}')

# Added "state" since without, "dot char at" is seen separately as "dot" and "char at" (versus combined command)
state <user.code_type> <user.letter>:           insert('{code_type} {letter}')
state <user.code_type> <user.text_code_codesaway>: insert('{code_type} {user.formatted_text(text_code_codesaway, "SNAKE_CASE")}')

# Couldn't find way to insert "not" for negation
op not:                                         insert('not ')
type int:                                       insert('int')

state pass:                                     "pass"

for <user.text_code_codesaway> in <user.text_code_codesaway>:
    variable = user.formatted_text(text_code_codesaway_1, 'SNAKE_CASE')
    iterable = user.formatted_text(text_code_codesaway_2, 'SNAKE_CASE')
    insert("for {variable} in {iterable}")

if <user.text_code_codesaway>:
    user.insert_between("if {text_code_codesaway}", ":")

else if <user.text_code_codesaway>:
    user.insert_between("elif {text_code_codesaway}", ":")

<user.text_code_codesaway> dot <user.text_code_codesaway>:
    variable = user.formatted_text(text_code_codesaway_1, 'SNAKE_CASE')
    member = user.formatted_text(text_code_codesaway_2, 'SNAKE_CASE')
    insert("{variable}.{member}")
