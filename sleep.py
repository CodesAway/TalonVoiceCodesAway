# https://talon.wiki/basic_customization/#turn-off-talon-listening-on-start-up
from talon import app, actions


def on_ready():
    actions.speech.disable()


app.register("ready", on_ready)
