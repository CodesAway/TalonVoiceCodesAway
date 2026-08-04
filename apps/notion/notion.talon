app: notion
-    
# Workaround to ensure arrow navigation is reliable
settings():
    key_wait = 15

this highlight: key("ctrl-shift-h")
language {user.notion_language}: 
    key("ctrl-/")
    sleep(100ms)
    insert(notion_language)
    sleep(100ms)
    key(enter)

page new : 
    insert("/page")
    key(enter)

block delete: 
    key("ctrl-/")
    sleep(100ms)
    insert("delete")
    sleep(100ms)
    key(enter)

callout new: 
    insert("/callout")
    key(enter)

background set {user.notion_color}:
    insert("/background {notion_color}")
    key(enter)