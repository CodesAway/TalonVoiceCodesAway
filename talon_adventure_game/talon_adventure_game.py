from talon import Module, cron, ui
from talon.canvas import Canvas
from talon.skia import Paint, Rect
from talon.skia.canvas import Canvas as SkiaCanvas

mod = Module()


def calculate_bottom_border(paint: Paint):
    """Calculates bottom border used for letters which appear below baseline"""
    # Workaround for paint.measure_text, which doesn't factor this in
    letters = ["g", "j", "p", "q", "y"]
    bottom_border = 0

    for letter in letters:
        rect: Rect = paint.measure_text(letter)[1]
        bottom_border = max(bottom_border, rect.y + rect.height)

    return bottom_border


@mod.action_class
class Actions:
    def tag_game_show_center_text(screen: ui.Screen, text: str):
        """Shows text for tag game in center of screen"""

        # Reference: community\core\screens\screens.py -> show_screen_number,
        def on_draw(c: SkiaCanvas):
            paint: Paint = c.paint

            paint.typeface = "arial"
            # The min(width, height) is to not get gigantic size on portrait screens
            paint.textsize = round(min(c.width, c.height) / 8)

            rect: Rect
            something, rect = paint.measure_text(text)
            bottom_border = calculate_bottom_border(paint)

            x = c.x + c.width / 2 - rect.x - rect.width / 2
            y = c.y + c.height / 2 + rect.height / 2

            border_size = c.paint.textsize / 5

            card_rect = Rect(
                x - border_size,
                y - rect.height - border_size,
                rect.width + 2 * border_size,
                rect.height + 2 * border_size + bottom_border,
            )

            paint.style = paint.Style.FILL
            paint.color = "663399"  # Rebecca purple
            c.draw_rect(card_rect)

            paint.style = paint.Style.FILL
            paint.color = "33b2cd"  # Amy's blue color
            c.draw_text(text, x, y)

            cron.after("3s", canvas.close)

        canvas = Canvas.from_screen(screen)
        canvas.register("draw", on_draw)
        canvas.freeze()
