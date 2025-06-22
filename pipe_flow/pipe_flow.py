from collections import deque

from talon import Module, app

mod = Module()

# Create a queue
flow_queue: deque[str] = deque()


@mod.action_class
class Actions:
    def fill_flow(text: str):
        "Fills the flow with the specified text (for later use)"
        flow_queue.append(text)

    # TODO: how to handle if flow_queue is empty? (currently shows error, which I think is correct)
    def fetch_flow() -> str:
        "Fetches the flow text"
        app.notify("Cannot fetch from flow (since empty)")
        return flow_queue.popleft()
