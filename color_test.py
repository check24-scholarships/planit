
import colour


def create_gradient(colors, steps_per_color=5):
    if len(colors) == 0:
        return []

    if len(colors) == 1:
        return [colors[0]] * steps_per_color

    gradient = []

    start = colour.Color(colors[0])
    for color in colors[1:]:
        color = colour.Color(color)
        gradient.extend(start.range_to(color, steps_per_color))
        start = color

    return gradient


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


def create_gradient_2(colors, steps_per_color=5):
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


gradient = create_gradient(["#e64369", "#f5c651", "#4ed46d"], steps_per_color=5)
show_gradient(gradient)

gradient = create_gradient_2(["#e64369", "#f5c651", "#76d44e", "#40c791"], steps_per_color=3)
print([col.hex for col in gradient])
show_gradient(gradient)
