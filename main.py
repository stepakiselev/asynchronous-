import time
import curses
import asyncio
import random

from explosion import explode
from physics import update_speed
from run_fire import fire, show_game_over
from curses_tools import draw_frame, read_controls, get_frame_size
import itertools

from space_garbage import fill_orbit_with_garbage, load_file
import variables

TIC_TIMEOUT = 0.1
ELEMENTS = ["+", "*", ".", ":"]
TIC_RATE = 0.1
POS_MIN_Y = 1
POS_MIN_X = 1

rocket_frame_1 = load_file("text/rocket_frame_1.txt")
rocket_frame_2 = load_file("text/rocket_frame_2.txt")


async def go_to_sleep(seconds):
    iteration_count = int(seconds * 10)
    for _ in range(iteration_count):
        await asyncio.sleep(0)

async def animate_spaceship(canvas, y_axis, x_axis, frames):
    frame = itertools.cycle(frames)
    height, width = canvas.getmaxyx()
    current_frame = next(frame)

    row_speed = column_speed = 0

    size_y, size_x = get_frame_size(current_frame)
    row = round(y_axis) - round(size_y / 2)
    column = round(x_axis) - round(size_x / 2)

    while True:
        direction_y, direction_x, shot = read_controls(canvas)

        row_speed, column_speed = update_speed(row_speed, column_speed, direction_y, direction_x)
        row, column = row + row_speed, column + column_speed

        pos_max_y = (height - 1) - size_y
        pos_max_x = (width - 1) - size_x

        row, column = max(min(row, pos_max_y), POS_MIN_Y), max(min(column, pos_max_x), POS_MIN_X)

        for obstacle in variables.obstacles:
            if obstacle.has_collision(round(row), round(column)):
                variables.obstacles_in_last_collisions.append(obstacle)
                variables.garbage_coroutines.append(show_game_over(canvas, height, width))
                await explode(canvas, round(row), round(column))
                # variables.garbage_coroutines.append(show_game_over(canvas, height, width))
                return

        draw_frame(canvas, row, column, current_frame)
        if shot:
            variables.garbage_coroutines.append(fire(canvas, row, column + 2))
        canvas.refresh()

        await go_to_sleep(TIC_RATE)

        draw_frame(canvas, row, column, current_frame, negative=True)

        current_frame = next(frame)

      
async def blink(canvas, y_axis, x_axis, symbol, sequence=1):
    while True:
        if sequence == 0:
            canvas.addstr(y_axis, x_axis, symbol, curses.A_DIM)
            await go_to_sleep(2)
            sequence += 1

        if sequence == 1:
            canvas.addstr(y_axis, x_axis, symbol)
            await go_to_sleep(0.3)
            sequence += 1

        if sequence == 2:
            canvas.addstr(y_axis, x_axis, symbol, curses.A_BOLD)
            await go_to_sleep(0.5)
            sequence += 1

        if sequence == 3:
            canvas.addstr(y_axis, x_axis, symbol)
            await go_to_sleep(0.3)
            sequence = 0

      
def create_stars(latitude, longitude, number=50):
    for _ in range(number):
        y_axis = random.randint(1, latitude - 2)
        x_axis = random.randint(1, longitude - 2)
        element = random.choice(ELEMENTS)
        yield y_axis, x_axis, element

  
def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)
    height, width = canvas.getmaxyx()
    few_frame = [rocket_frame_1, rocket_frame_2]

    start_y = height - 5
    start_x =  width / 2
  
    stars = [
        blink(canvas, y_axis, x_axis, symbol, random.randint(0, 3))
        for y_axis, x_axis, symbol in create_stars(height, width)
    ]

    for star in stars:
       variables.garbage_coroutines.append(star)

    variables.garbage_coroutines.append(animate_spaceship(canvas, start_y, start_x, few_frame)) # добавил выстрел
    variables.garbage_coroutines.append(fill_orbit_with_garbage(canvas, width))
    while True:
        for value in variables.garbage_coroutines[:]:
            try:
                value.send(None)
            except StopIteration:
                variables.garbage_coroutines.remove(value)
            except Exception as e:
                print(f"Error in coroutine: {e}")
        canvas.refresh()
        # time.sleep(TIC_TIMEOUT)
        # Замена time.sleep на curses.napms
        curses.napms(int(TIC_TIMEOUT * 1000))

if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
    # for i in variables.log:
    #     print(i)
