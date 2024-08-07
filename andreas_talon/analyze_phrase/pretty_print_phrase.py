# https://github.com/AndreasArvidsson/andreas-talon/blob/master/core/on_phrase/pretty_print_phrase.py
from talon import Module, settings

from .types import AnalyzedPhrase

mod = Module()

mod.setting(
    "pretty_print_phrase",
    type=bool,
    default=False,
    desc="If true phrase will be pretty printed to the log",
)


def pretty_print_phrase(analyzed_phrase: AnalyzedPhrase):
    """Pretty prints the analyzed phrase and its commands"""
    if not settings.get("user.pretty_print_phrase"):
        return

    print(f"{bcolors.ENDC}=============================={bcolors.ENDC}")
    print(
        f"{bcolors.BOLD}Phrase:{bcolors.ENDC} {bcolors.GREEN}{bcolors.BOLD}{analyzed_phrase.phrase}{bcolors.ENDC}"
    )

    for i, cmd in enumerate(analyzed_phrase.commands):
        printLine(
            f"#{i + 1}:",
            f"{bcolors.BOLD}{cmd.phrase}{bcolors.ENDC}",
            f"{cmd.path} {bcolors.GREEN}{cmd.rule}{bcolors.ENDC}",
        )
        for action in cmd.actions:
            printLine(
                f"  {bcolors.BOLD}{action.name}{bcolors.ENDC}:",
                f"{action.explanation}",
            )

    print(f"{bcolors.ENDC}=============================={bcolors.ENDC}")


def printLine(*argv):
    print(" ".join(argv))


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    RED = "\033[31m"
    GREEN = "\033[92m"
