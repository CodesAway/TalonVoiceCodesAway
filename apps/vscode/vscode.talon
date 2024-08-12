app: vscode
os: windows
-
# Reference: community\apps\vscode\vscode.talon

# Overrides command from community
focus editor:
    user.vscode("workbench.action.focusActiveEditorGroup")
    # Commands from Auto Hide extension
    user.vscode("closeReferenceSearch")
    user.vscode("workbench.action.closePanel")
    user.vscode("workbench.action.closeSidebar")
    user.vscode("workbench.action.closeAuxiliaryBar")

tutorial focus:                                 user.vscode("cursorless.tutorial.focus")

lower case:                                     user.vscode("editor.action.transformToLowercase")
settings open:                                  key("ctrl-,")
save sin:                                       user.vscode("workbench.action.files.saveWithoutFormatting")

# Workaround since VSCode is only app which standard maximize doesn't seem to work
# Requires changing PowerToys Run command (switched to Win-space)
maximize:
    key("alt-space")
    sleep(100ms)
    key("up:2 enter")

slot {self.letter} [{self.letter}]:
    user.run_rpc_command("andreas.focusTab", "{letter_1}{letter_2 or ''}")

# Reference: community\apps\vscode\vscode.talon (used similiar grammar as Rango)
tab close other:                                user.vscode("workbench.action.closeOtherEditors")
tab close all:                                  user.vscode("workbench.action.closeAllEditors")

this run:                                       user.vscode_run_active()

terminal open:                                  user.vscode("workbench.action.terminal.focus")
terminal close:                                 user.vscode("workbench.action.terminal.kill")
terminal close all:                             user.vscode("workbench.action.terminal.killAll")

# Can also use Cursorless `follow <target>`
link open:                                      user.vscode("editor.action.openLink")

case switch:                                    user.find_toggle_match_by_case()
regex switch:                                   user.find_toggle_match_by_regex()

view (last | previous | prev | up):             key(ctrl-up)
view (next | down):                             key(ctrl-down)

group (last | previous | prev):                 user.vscode("workbench.action.focusPreviousGroup")
group next:                                     user.vscode("workbench.action.focusNextGroup")

recent editor (last | previous | prev):         user.vscode("workbench.action.openPreviousRecentlyUsedEditor")
recent editor next:                             user.vscode("workbench.action.openNextRecentlyUsedEditor")

part left:                                      user.vscode("cursorWordPartLeft")
part right:                                     user.vscode("cursorWordPartRight")

move up:                                        edit.line_swap_up()
move down:                                      edit.line_swap_down()

editor left:                                    key(ctrl-shift-pageup)
editor right:                                   key(ctrl-shift-pagedown)

none check <user.cursorless_target>:
    user.insert_snippet_with_cursorless_target("nullCheck", "1", cursorless_target)

search text [<user.text>]:
    user.vscode("search.action.focusQueryEditorWidget")
    sleep(100ms)
    insert(text or "")

search include [<user.text>]:
    user.vscode("search.action.focusFilesToInclude")
    sleep(100ms)
    insert(text or "")

search exclude [<user.text>]:
    user.vscode("search.action.focusFilesToExclude")
    sleep(100ms)
    insert(text or "")
