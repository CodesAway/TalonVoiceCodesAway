from talon import actions, Module, speech_system

mod = Module()


@mod.action_class
class Actions:
    def media_play_pause() -> None:
        """
        Play or pause media (overrides functionality in community)
        """
        # command = actions.core.last_command()[1]  # talon.grammar.vm.Capture
        # # String version is command said
        # # Used "dir" build-in command to check attributes and didn't see one that met my needs
        # command_text = str(command)
        command_text = last_phrase
        # print(f"media_play_pause@{command_text}@")

        if command_text == "media play":
            # Work around to ensure that media play keeps the music playing if it's already playing
            actions.key("stop")
            # Smallest increment of 25ms which consistently ensured the music would play
            actions.sleep("125ms")
            actions.user.play_pause()
        elif command_text == "media pause":
            actions.key("stop")
        else:
            print("Unknown media_play_pause:", command_text)


last_phrase = None


# Referenced: user\community\plugin\command_history\command_history.py
def on_phrase(j):
    global last_phrase

    words = j.get("text")

    text = actions.user.history_transform_phrase_text(words)
    last_phrase = text


speech_system.register("phrase", on_phrase)
