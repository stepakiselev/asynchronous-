from curses_tools import draw_frame
import asyncio
import os
import random
import time
import curses
import itertools
from curses_tools import get_frame_size
from obstacles import show_obstacles, Obstacle

TIC_TIMEOUT = 0.1
garbage_coroutines = []
obstacles = []


def load_file(filename):
    with open(filename, "r") as frame:
        return frame.read()

async def wait(seconds):
    iteration_count = int(seconds * 10)
    for _ in range(iteration_count):
        await asyncio.sleep(0)

def position_garbage(frame):
    _, column = get_frame_size(frame)
    return column
  

def create_garbages(canvas, garbages, number=1):
    rows_number, columns_number = canvas.getmaxyx()
    column = columns_number-1
    for garbage in range(number):
        element = random.choice(garbages)
        pos = random.randint(1, column)
        yield element, pos

async def fly_garbage(canvas, column, garbage_frame, speed=0.2):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0
    rows_size, columns_size = get_frame_size(garbage_frame)

    while row < rows_number:
        obstacle = Obstacle(row, column, rows_size, columns_size) # add
        obstacles.append(obstacle)  # add
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        obstacles.remove(obstacle) # add
        row += speed


async def fill_orbit_with_garbage(canvas, width):
  list_garbage_frame = os.listdir(path="garbage")

  garbages = [load_file(f"garbage/{garbage_frame}") for garbage_frame in list_garbage_frame]
  while True:
      pos = random.randint(1, width-1)
      element = random.choice(garbages)
      garbage_coroutines.append(fly_garbage(canvas, pos, element))
      garbage_coroutines.append(show_obstacles(canvas, obstacles)) # add
      await wait(2)
  
def some(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)

    height, width = canvas.getmaxyx()
    garbage_coroutines.append(fill_orbit_with_garbage(canvas, width))
    while True:
        for value in garbage_coroutines[:]:
            try:
                value.send(None)
            except StopIteration:
                garbage_coroutines.remove(value)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


curses.update_lines_cols()
curses.wrapper(some)
