code.language: markdown
-
# Reference community\lang\markdown\markdown.talon
graph new:
    edit.line_insert_down()
    edit.line_insert_down()

(level | heading | header) one <user.text>:
    edit.line_start()
    "# "
    user.insert_formatted(text, "CAPITALIZE_FIRST_WORD")
(level | heading | header) two <user.text>:
    edit.line_start()
    "## "
    user.insert_formatted(text, "CAPITALIZE_FIRST_WORD")
(level | heading | header) three <user.text>:
    edit.line_start()
    "### "
    user.insert_formatted(text, "CAPITALIZE_FIRST_WORD")
(level | heading | header) four <user.text>:
    edit.line_start()
    "#### "
    user.insert_formatted(text, "CAPITALIZE_FIRST_WORD")
(level | heading | header) five <user.text>:
    edit.line_start()
    "##### "
    user.insert_formatted(text, "CAPITALIZE_FIRST_WORD")
(level | heading | header) six <user.text>:
    edit.line_start()
    "###### "
    user.insert_formatted(text, "CAPITALIZE_FIRST_WORD")

list [one] <user.text>:
    edit.line_start()
    "- "
    user.insert_formatted(text, "CAPITALIZE_FIRST_WORD")
list two <user.text>:
    edit.line_start()
    "    - "
    user.insert_formatted(text, "CAPITALIZE_FIRST_WORD")
list three <user.text>:
    edit.line_start()
    "        - "
    user.insert_formatted(text, "CAPITALIZE_FIRST_WORD")
list four <user.text>:
    edit.line_start()
    "            - "
    user.insert_formatted(text, "CAPITALIZE_FIRST_WORD")
list five <user.text>:
    edit.line_start()
    "                - "
    user.insert_formatted(text, "CAPITALIZE_FIRST_WORD")
list six <user.text>:
    edit.line_start()
    "                    - "
    user.insert_formatted(text, "CAPITALIZE_FIRST_WORD")

{user.markdown_code_block_language} block:
    user.insert_snippet("```{markdown_code_block_language}\n$0\n```")

link:                                           user.insert_snippet_by_name("link")
