code.language: java
-
var <user.text>:            insert(user.reformat_text(text, "camel"))
class <user.text>:          insert(user.reformat_text(text, "hammer"))
<user.code_type> <user.text>: insert('{code_type} {user.reformat_text(text, "camel")}')
diamond <user.text>:        insert('{user.reformat_text(text, "hammer")}<>')
