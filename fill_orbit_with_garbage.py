from main import wait


async def fill_orbit_with_garbage(canvas, y_axis, x_axis, element, speed):
    while True:
        canvas.addstr(y_axis, x_axis, element, speed)
        await wait(2)

        y_axis += speed
        canvas.addstr(y_axis, x_axis, element, speed)
        await wait(2)
