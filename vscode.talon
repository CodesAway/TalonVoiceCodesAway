app: vscode
os: windows
-
# Overrides command from community
focus editor:
    user.vscode("workbench.action.focusActiveEditorGroup")
    # Commands from Auto Hide extension
    user.vscode("closeReferenceSearch")
    user.vscode("workbench.action.closePanel")
    user.vscode("workbench.action.closeSidebar")
    user.vscode("workbench.action.closeAuxiliaryBar")

lower case:                 user.vscode("editor.action.transformToLowercase")
settings open:              key("ctrl-,")

find <user.text>$:
    user.vscode("actions.find")
    sleep(50ms)
    insert(text or "")
