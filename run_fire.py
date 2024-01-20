import asyncio
import curses
import variables
import logging
import os

from frame import load_file, draw_frame, get_frame_size
from explosion import explode


logging.basicConfig(
    filename='app.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)


DEFAULT_ROW_SPEED = -0.8
DEFAULT_COLUMN_SPEED = 0
BULLET_SPEED_DELAY = 0


async def show_game_over(canvas, rows_number, columns_number):
    """
    Show 'Game Over' text animation in the canvas.

    :param canvas: The canvas where the text will be shown.
    :param rows_number: Number of rows in the canvas.
    :param columns_number: Number of columns in the canvas.
    """
    text_dir = "text"
    if not os.path.exists(text_dir) or not os.listdir(text_dir):
        logging.error(f"Directory '{text_dir}' is missing or empty.")
        return  # Завершаем программу, если директория отсутствует или пуста

    game_over_frame = load_file("text/game_over.txt")
    rows, columns = get_frame_size(game_over_frame)

    rows_middle, columns_middle = (rows_number/2)-rows/2, (columns_number/2)-columns/2
    while True:
        draw_frame(canvas, rows_middle, columns_middle, game_over_frame)
        await asyncio.sleep(0)
        draw_frame(
            canvas,
            rows_middle,
            columns_middle,
            game_over_frame,
            negative=True
        )


async def fire(canvas, start_row, start_column, rows_speed=DEFAULT_ROW_SPEED, columns_speed=DEFAULT_COLUMN_SPEED):
    """
    Display animation of a gun shot with specified direction and speed.

    :param canvas: The canvas where the shot will be animated.
    :param start_row: The starting row position of the shot.
    :param start_column: The starting column position of the shot.
    :param rows_speed: Vertical speed of the shot.
    :param columns_speed: Horizontal speed of the shot.
    """
    row, column = start_row, start_column

    # Проверка, не выходит ли начальная позиция пули за пределы холста
    max_row, max_column = canvas.getmaxyx()
    if not (0 < row < max_row and 0 < column < max_column):
        return  # Выход из функции, если начальная позиция вне холста

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(BULLET_SPEED_DELAY)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(BULLET_SPEED_DELAY)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        for obstacle in variables.obstacles:
            if obstacle.has_collision(round(row), round(column)):
                variables.obstacles_in_last_collisions.append(obstacle)
                await explode(canvas, round(row), round(column))
                return

        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(BULLET_SPEED_DELAY)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed
