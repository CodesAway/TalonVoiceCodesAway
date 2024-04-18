import re
from talon import Module, actions, ui

mod = Module()


@mod.action_class
class Actions:
    def vscode_run_active():
        """
        Run active file in VSCode
        """
        vscode = ui.active_window()
        title = vscode.title
        if re.search(r"(?:\.sql|Untitled-\d+).*(?<=- Visual Studio Code)$", title):
            print("TODO: Implement SQL: ctrl-shift-e...")
        elif re.search(r"\.java.*(?<=- Visual Studio Code)$", title):
            print("Run Java:", title)
            actions.user.vscode("java.debug.runJavaFile")
        elif re.search(r"\.py.*(?<=- Visual Studio Code)$", title):
            print("Run Python:", title)
            actions.user.vscode("python.execInTerminal")
        else:
            print(vscode.app.exe)
            print(title)
            # Terminal: Run Active File In Active Terminal
            actions.user.vscode("workbench.action.terminal.runActiveFile")
