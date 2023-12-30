import asyncio
import logging
import random

import variables
from frame import get_frames, draw_frame, get_frame_size
from obstacles import Obstacle

TIC_TIMEOUT = 0.1
DEFAULT_SPEED = 0.2
MAX_SLEEP_TIME = 0  # если поставить значение больше нуля все поламается

# Logging configuration
logging.basicConfig(
    filename='app.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

def get_garbage_delay_tic(year):
    """
    Calculate the delay for garbage appearance based on the year.

    :param year: Year to determine the rate of garbage appearance.
    :return: Delay in ticks until the next appearance of garbage.
    """
    if year < 1961:
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


async def wait(seconds):
    """
    Asynchronously wait for a given number of seconds.

    :param seconds: Number of seconds to wait.
    """
    iteration_count = int(seconds * 10)
    for _ in range(iteration_count):
        await asyncio.sleep(0)


def position_garbage(frame):
    """
    Get the position for placing garbage on the canvas.

    :param frame: Frame of the garbage.
    :return: Column for placing the garbage.
    """
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
        logging.error(f"Error in fly_garbage: {e}", exc_info=True)
    finally:
        # Убеждаемся, что препятствие удаляется при завершении анимации
        if obstacle in variables.obstacles:
            variables.obstacles.remove(obstacle)


async def fill_orbit_with_garbage(canvas, width):
    """
    Continuously fill the orbit with garbage.

    :param canvas: Canvas for drawing.
    :param width: Width of the canvas.
    """
    garbages = get_frames("garbage/")
    amount = 3  # начальное количество мусора
    max_amount = 10  # максимальное количество мусора
    try:
        while True:
            delay_factor = get_garbage_delay_tic(variables.year)
            sleep_time = delay_factor / 10  # преобразование задержки

            garbage_count = random.randint(1, min(amount, max_amount))
            for _ in range(garbage_count):
                column = random.randint(1, width - 1)
                garbage_frame = random.choice(garbages)
                variables.garbage_coroutines.append(fly_garbage(canvas, column, garbage_frame))

            await wait(sleep_time)
            # Увеличение количества мусора с ограничением
            amount = min(amount + 2, max_amount)
    except Exception as e:
        logging.error(f"Error in fill_orbit_with_garbage: {e}", exc_info=True)
