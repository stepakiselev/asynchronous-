import asyncio
import os
import random

import variables
from curses_tools import draw_frame
from curses_tools import get_frame_size
from obstacles import Obstacle

TIC_TIMEOUT = 0.1
DEFAULT_SPEED = 0.2
MAX_SLEEP_TIME = 0  # если поставить значение больше нуля все поламается


def get_garbage_delay_tic(year):
    if year < 1961:
        # return None
        return 30
    elif year < 1969:
        return 20
    elif year < 1981:
        return 14
    elif year < 1995:
        return 10
    elif year < 2010:
        return 8
    elif year < 2020:
        return 6
    else:
        return 2

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
        level = get_garbage_delay_tic(variables.year)/10
        amount = 3  # количество мусора на старте
        for _ in range(1, random.randint(1, amount)):
            variables.garbage_coroutines.append(
                fly_garbage(
                    canvas,
                    random.randint(1, width-1),
                    random.choice(garbages)
                )
            )
        await wait(level)
        amount += 2
