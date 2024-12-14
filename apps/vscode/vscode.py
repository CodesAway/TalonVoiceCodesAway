import logging
import re

from talon import Module, actions, clip, ui

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

    def get_vscode_cursor_position():
        """Gets VSCode cursor position"""

        # Based on logic in dictation_peek, except uses undo instead of delete
        # (in case something was selected, don't want to delete it)
        actions.insert(" ")
        actions.edit.extend_word_left()
        actions.edit.extend_word_left()
        before = actions.edit.selected_text()[:-1]
        actions.edit.right()
        # Undo insertion of blank (also handles if there was selected text)
        actions.edit.undo()
        # Added short sleep since sometimes noticed incorrect position without (guess if undo takes a bit??)
        actions.sleep("200ms")

        if before:
            # Used instead of ctrl-shift-home (so that doesn't change screen scroll)
            # (works great unless at beginning of file...then selects to end of line, which isn't what I want)
            # (used above workaround to check for text before)
            actions.user.vscode_with_plugin("andreas.selectTo", 0)

            with clip.capture() as text_capture:
                actions.edit.copy()

            # Added short sleep since sometimes noticed text remained selected without sleep
            actions.sleep("50ms")
            actions.edit.right()

            text: str = text_capture.text()
            lines = text.splitlines(keepends=True)
            row = len(lines)
            col = len(lines[-1]) + 1

            # Handle if cursor is on start of line
            if lines[-1].endswith("\n"):
                row += 1
                col = 1
        else:
            row = 1
            col = 1

        print(f"Ln {row}, Col {col}")

    # def get_cursorless_position(target: CursorlessTarget):
    #     """Gets cursor position for Cursorless target"""
    #     destination = actions.user.cursorless_create_destination(target)
    #     actions.user.cursorless_insert()

    #     mark = target.mark

    #     print(type(mark))
    #     print(target.mark)
    #     print(destination)
