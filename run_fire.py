import asyncio
import curses
import variables

# Константы для управления скоростью пули
DEFAULT_ROW_SPEED = -0.8
DEFAULT_COLUMN_SPEED = 0
BULLET_SPEED_DELAY = 0  # Добавлено задержку для контроля скорости пули


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
                    return

            canvas.addstr(round(row), round(column), symbol)
            await asyncio.sleep(BULLET_SPEED_DELAY)
            canvas.addstr(round(row), round(column), ' ')
            row += rows_speed
            column += columns_speed
    except Exception as e:
        # Вывод сообщения об ошибке в консоль
        print(f"Error in fire function: {e}")
