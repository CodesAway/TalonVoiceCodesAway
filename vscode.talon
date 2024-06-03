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

# Workaround since VSCode is only app which standard maximize doesn't seem to work
# Requires changing PowerToys Run command (switched to Win-space)
maximize:
    key("alt-space")
    sleep(100ms)
    key("up:2 enter")

slot {self.letter} [{self.letter}]:
    user.run_rpc_command("andreas.focusTab", "{letter_1}{letter_2 or ''}")

this run:                   user.vscode_run_active()
terminal close:             user.vscode("workbench.action.terminal.kill")
terminal close all:         user.vscode("workbench.action.terminal.killAll")
regex switch:               user.find_toggle_match_by_regex()

view (next | down):         key(ctrl-down)
view (last | previous | prev | up): key(ctrl-up)
