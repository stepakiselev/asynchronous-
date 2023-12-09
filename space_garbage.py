from curses_tools import draw_frame
import asyncio
import os
import random
import time
import curses
import itertools
from curses_tools import get_frame_size
from obstacles import show_obstacles, Obstacle
import variables

TIC_TIMEOUT = 0.1
DEFAULT_SPEED = 0.2
MAX_SLEEP_TIME = 0  # если поставить значение больше нуля все поламается


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

async def fly_garbage(canvas, column, garbage_frame, speed=DEFAULT_SPEED):
    """
    Animate garbage, flying from top to bottom. Column position will stay same, as specified on start.

    :param canvas: Canvas to draw the garbage.
    :param column: Column in which the garbage will fly.
    :param garbage_frame: Frame representation of the garbage.
    :param speed: Speed of the garbage movement, defaults to 0.2.
    """
    try:
        rows_number, columns_number = canvas.getmaxyx()

        # Обеспечиваем, что мусор остаётся в пределах холста
        column = max(min(column, columns_number - 1), 0)

        row = 0
        rows_size, columns_size = get_frame_size(garbage_frame)

        # Создание и добавление препятствия
        obstacle = Obstacle(row, column, rows_size, columns_size)
        variables.obstacles.append(obstacle)

        while row < rows_number:
            # Проверка на столкновение с пулей
            if obstacle in variables.obstacles_in_last_collisions:
                variables.obstacles.remove(obstacle)
                variables.obstacles_in_last_collisions.clear()
                return  # Препятствие уничтожено, завершаем анимацию

            draw_frame(canvas, row, column, garbage_frame)

            # Ожидание с учётом скорости
            sleep_time = min(MAX_SLEEP_TIME, 1 / speed)
            await asyncio.sleep(sleep_time)

            draw_frame(canvas, row, column, garbage_frame, negative=True)
            row += speed
            # Обновление позиции препятствия
            obstacle.row = row

    except Exception as e:
        # Обработка возможных исключений
        print(f"Error during garbage animation: {e}")
    finally:
        # Убеждаемся, что препятствие удаляется при завершении анимации
        if obstacle in variables.obstacles:
            variables.obstacles.remove(obstacle)


async def fill_orbit_with_garbage(canvas, width):
  list_garbage_frame = os.listdir(path="garbage")

  garbages = [load_file(f"garbage/{garbage_frame}") for garbage_frame in list_garbage_frame]
  while True:
      pos = random.randint(1, width-1)
      element = random.choice(garbages)
      variables.garbage_coroutines.append(fly_garbage(canvas, pos, element))
      variables.garbage_coroutines.append(show_obstacles(canvas, variables.obstacles)) # add
      await wait(2)
  
def some(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)

    height, width = canvas.getmaxyx()
    variables.garbage_coroutines.append(fill_orbit_with_garbage(canvas, width))
    while True:
        for value in variables.garbage_coroutines[:]:
            try:
                value.send(None)
            except StopIteration:
                variables.garbage_coroutines.remove(value)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)

        # # Замена time.sleep на curses.napms
        # curses.napms(int(TIC_TIMEOUT * 1000))


# curses.update_lines_cols()
# curses.wrapper(some)
