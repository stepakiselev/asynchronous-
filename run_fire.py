import asyncio
import curses
import variables

from curses_tools import draw_frame, get_frame_size
from explosion import explode
from space_garbage import load_file

DEFAULT_ROW_SPEED = -0.8
DEFAULT_COLUMN_SPEED = 0
BULLET_SPEED_DELAY = 0


async def show_game_over(canvas, rows_number, columns_number):
    try:
        game_over_frame = load_file("text/game_over.txt")
        rows, columns = get_frame_size(game_over_frame)

        rows_middle, columns_middle = (rows_number/2)-rows/2, (columns_number/2)-columns/2
        while True:
            draw_frame(canvas, rows_middle, columns_middle, game_over_frame)
            await asyncio.sleep(0)
            draw_frame(canvas, rows_middle, columns_middle, game_over_frame, negative=True)
    except Exception as e:
        print(f"Error in fire function: {e}")


async def fire(canvas, start_row, start_column, rows_speed=DEFAULT_ROW_SPEED, columns_speed=DEFAULT_COLUMN_SPEED):
    """Display animation of gun shot, direction and speed can be specified."""
    try:
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
    except Exception as e:
        print(f"Error in fire function: {e}")
