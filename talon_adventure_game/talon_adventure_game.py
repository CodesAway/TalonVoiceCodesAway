from talon import Module, cron, ui
from talon.canvas import Canvas
from talon.skia import Rect
from talon.skia.canvas import Canvas as SkiaCanvas

mod = Module()


@mod.action_class
class Actions:
    def tag_game_show_text(screen: ui.Screen, text: str):
        """Shows text for tag game in center of screen"""

        # Reference: community\core\screens\screens.py -> show_screen_number,
        def on_draw(c: SkiaCanvas):
            c.paint.typeface = "arial"
            # The min(width, height) is to not get gigantic size on portrait screens
            c.paint.textsize = round(min(c.width, c.height) / 8)
            rect: Rect = c.paint.measure_text(text)[1]
            x = c.x + c.width / 2 - rect.x - rect.width / 2
            y = c.y + c.height / 2 + rect.height / 2

            border_size = c.paint.textsize / 5

            card_rect = Rect(
                x - border_size,
                y - rect.height - border_size,
                rect.width + 2 * border_size,
                rect.height + 2 * border_size,
            )

            c.paint.style = c.paint.Style.FILL
            c.paint.color = "663399"  # Rebecca purple
            c.draw_rect(card_rect)

            c.paint.style = c.paint.Style.FILL
            c.paint.color = "33b2cd"  # Amy's blue color
            c.draw_text(text, x, y)

            cron.after("3s", canvas.close)

        canvas = Canvas.from_screen(screen)
        canvas.register("draw", on_draw)
        canvas.freeze()
