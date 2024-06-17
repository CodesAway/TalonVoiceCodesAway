import logging
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
            logging.warning("TODO: Implement SQL: ctrl-shift-e...")
        elif re.search(r"\.java.*(?<=- Visual Studio Code)$", title):
            logging.debug(f"Run Java: {title}")
            actions.user.vscode("java.debug.runJavaFile")
        elif re.search(r"\.py.*(?<=- Visual Studio Code)$", title):
            logging.debug(f"Run Python: {title}")
            actions.user.vscode("python.execInTerminal")
        else:
            logging.debug(vscode.app.exe)
            logging.debug(title)
            # Terminal: Run Active File In Active Terminal
            actions.user.vscode("workbench.action.terminal.runActiveFile")
