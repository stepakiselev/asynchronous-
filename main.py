import time
import curses
import asyncio
import random

from physics import update_speed
from run_fire import fire
from curses_tools import draw_frame, read_controls, get_frame_size
import itertools

from space_garbage import fill_orbit_with_garbage, some
import variables

TIC_TIMEOUT = 0.1
ELEMENTS = ["+", "*", ".", ":"]
# animate = [] # add for fire

with open("rocket_frame_1.txt", "r") as frame_1:
    rocket_frame_1 = frame_1.read()


with open("rocket_frame_2.txt", "r") as frame_2:
    rocket_frame_2 = frame_2.read()


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
    pos_starship_y = round(y_axis) - round(size_y/2)
    pos_starship_x = round(x_axis) - round(size_x/2)
  
    while True:
        direction_y, direction_x, shot = read_controls(canvas)

        row_speed, column_speed = update_speed(row_speed, column_speed, direction_y, direction_x)
        pos_starship_y, pos_starship_x = pos_starship_y + row_speed, pos_starship_x + column_speed

        pos_max_y = (height - 1) - size_y
        pos_max_x = (width - 1) - size_x
        pos_min_y = 1
        pos_min_x = 1

        pos_starship_y = min(pos_starship_y, pos_max_y)
        pos_starship_x = min(pos_starship_x, pos_max_x)
    
        pos_starship_y = max(pos_starship_y, pos_min_y)
        pos_starship_x = max(pos_starship_x, pos_min_x)
    
        draw_frame(canvas, pos_starship_y, pos_starship_x, current_frame)
        if shot:
            variables.garbage_coroutines.append(fire(canvas, pos_starship_y, pos_starship_x+2))  # pos_starship_x+2 чтобы выстрел был из середины
        canvas.refresh()
    
        await go_to_sleep(0.1)

        draw_frame(canvas, pos_starship_y, pos_starship_x, current_frame, negative=True)

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

    run_spaceship = animate_spaceship(canvas, start_y, start_x, few_frame)
    variables.garbage_coroutines.append(run_spaceship) # добавил выстрел
    variables.garbage_coroutines.append(fill_orbit_with_garbage(canvas, width))

    while True:
        for value in variables.garbage_coroutines[:]:
            try:
                value.send(None)
            except StopIteration:
                variables.garbage_coroutines.remove(value)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)

if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
