
"""
Helper script that smooths the quality color gradient in the theme.
"""


from .theme import theme
import colour


def linspace(start, stop, num=50, include_endpoint=True):
    num = int(num)
    if num == 0:
        return []

    if num == 1:
        yield stop if include_endpoint else start

    if include_endpoint:
        step = (stop - start) / (num - 1)
    else:
        step = (stop - start) / num

    for i in range(num):
        yield start + step * i


def create_gradient(colors, steps_per_color=5):
    gradient = []
    colors = list(colour.Color(color) for color in colors)

    start = colors[0]
    for color in colors[1:]:
        r0, g0, b0 = start.rgb
        r1, g1, b1 = color.rgb

        r_values = linspace(r0, r1, steps_per_color, include_endpoint=False)
        g_values = linspace(g0, g1, steps_per_color, include_endpoint=False)
        b_values = linspace(b0, b1, steps_per_color, include_endpoint=False)

        gradient.extend(colour.Color(rgb=(r, g, b)) for r, g, b in zip(r_values, g_values, b_values))
        start = color

    gradient.append(colors[-1])
    return gradient


def show_gradient(colors):
    import tkinter as tk

    root = tk.Tk()
    canvas = tk.Canvas()
    canvas.pack(fill=tk.BOTH, expand=True)

    SIZE = 50
    for i, color in enumerate(colors):
        canvas.create_rectangle(i * SIZE, 0, i * SIZE + SIZE, SIZE, fill=color, width=0)

    root.mainloop()


quality_settings = theme.beet_view.cell.quality


QUALITY_COLORS = [
    color.hex
    for color
    in create_gradient(quality_settings.gradient, steps_per_color=quality_settings.gradient_smoothing)
]
