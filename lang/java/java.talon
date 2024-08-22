code.language: java
-
# TODO: cache list of variables?
# That way return could reference the existing variables (versus trying to create new)
# Similarly, could have separate commands to create a variable versus reference a variable

dot <user.text_code_codesaway>:                 insert('.{user.formatted_text(text_code_codesaway, "PRIVATE_CAMEL_CASE")}')
var <user.text_code_codesaway>:                 insert(user.formatted_text(text_code_codesaway, "PRIVATE_CAMEL_CASE"))
# Extends what's in functions.talon to allow customize types (basic types in java.py)
type <user.text_code_codesaway>:                insert(user.formatted_text(text_code_codesaway, "PUBLIC_CAMEL_CASE"))
no args:                                        insert('()')
return <user.text_code_codesaway>:              insert('return {user.formatted_text(text_code_codesaway, "PRIVATE_CAMEL_CASE")}')
# Added "state" since without, "dot char at" is seen separately as "dot" and "char at" (versus combined command)
state <user.code_type> <user.letter>:           insert('{code_type} {letter}')
state <user.code_type> <user.text_code_codesaway>: insert('{code_type} {user.formatted_text(text_code_codesaway, "PRIVATE_CAMEL_CASE")}')
# Use defined types (handles HashMap correctly versus Hashmap)
diamond <user.code_type>:                       insert('{code_type}<>')
diamond <user.text_code_codesaway>:             insert('{user.formatted_text(text_code_codesaway, "PUBLIC_CAMEL_CASE")}<>')
