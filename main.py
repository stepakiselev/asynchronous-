import curses
import itertools
import logging
import random

import variables
from curses_tools import read_controls
from explosion import explode
from frame import get_frames, draw_frame, get_frame_size
from game_scenario import show_phrases
from physics import update_speed
from run_fire import fire, show_game_over
from space_garbage import fill_orbit_with_garbage, wait

logging.basicConfig(
    filename='app.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

TIC_TIMEOUT = 0.1
ELEMENTS = ["+", "*", ".", ":"]
TIC_RATE = 0.1
POS_MIN_Y = 1
POS_MIN_X = 1
TIME_PHASE = 5


async def animate_spaceship(canvas, height, width):
    """
    Generate random positions and symbols for stars.

    :param canvas: Canvas on which the star will be drawn.
    :param height: Maximum Y-axis value for star positions.
    :param width: Maximum X-axis value for star positions.
    :return: Yields tuples of (y_axis, x_axis, symbol) for each star.
    """
    # ship changes animation every second beat
    frames = sum(map(lambda x: [x, x], get_frames("text/rocket_frame/")), [])

    row_speed = column_speed = 0
    frame = itertools.cycle(frames)
    current_frame = next(frame)

    size_y, size_x = get_frame_size(current_frame)
    row = round(height - 5) - round(size_y / 2)
    column = round(width / 2) - round(size_x / 2)
    while True:
        try:
            direction_y, direction_x, shot = read_controls(canvas)

            row_speed, column_speed = update_speed(
                row_speed, column_speed, direction_y, direction_x
            )
            row, column = row + row_speed, column + column_speed

            pos_max_y, pos_max_x = (height - 1) - size_y, (width - 1) - size_x

            row = max(min(row, pos_max_y), POS_MIN_Y)
            column = max(min(column, pos_max_x), POS_MIN_X)
            for obstacle in variables.obstacles:
                if obstacle.has_collision(round(row), round(column)):
                    variables.obstacles_in_last_collisions.append(obstacle)
                    variables.garbage_coroutines.append(
                        show_game_over(canvas, height, width)
                    )
                    await explode(canvas, round(row), round(column))
                    return

            draw_frame(canvas, row, column, current_frame)
            if shot:
                variables.garbage_coroutines.append(
                    fire(canvas, row, column + 2)
                )

            await wait(TIC_RATE)

            draw_frame(canvas, row, column, current_frame, negative=True)

            current_frame = next(frame)
        except Exception as e:
            logging.error(
                f"Error in animate_spaceship function: {e}", exc_info=True
            )


async def blink(canvas, y_axis, x_axis, symbol, sequence=1):
    """
    Animate a blinking star at a given position on the canvas.

    This function handles the animation of a single star.
    The star will cycle through
    different brightness states to create a blinking effect.

    :param canvas: Canvas on which the star will be drawn.
    :param y_axis: The Y-axis position of the star on the canvas.
    :param x_axis: The X-axis position of the star on the canvas.
    :param symbol: The symbol used to represent the star.
    :param sequence: The initial state of the blinking sequence.
    """
    while True:
        try:
            if sequence == 0:
                canvas.addstr(y_axis, x_axis, symbol, curses.A_DIM)
                await wait(2)
                sequence += 1

            if sequence == 1:
                canvas.addstr(y_axis, x_axis, symbol)
                await wait(0.3)
                sequence += 1

            if sequence == 2:
                canvas.addstr(y_axis, x_axis, symbol, curses.A_BOLD)
                await wait(0.5)
                sequence += 1

            if sequence == 3:
                canvas.addstr(y_axis, x_axis, symbol)
                await wait(0.3)
                sequence = 0
        except Exception as e:
            logging.error(f"Error in blink function: {e}", exc_info=True)


def create_stars(latitude, longitude, number=50):
    """
    Create a specified number of stars at random positions.

    This function generates random positions and characters
    for stars to be displayed on the canvas.
    Each star is represented by a tuple containing its position and symbol.

    :param latitude: The height of the canvas where stars will be placed.
    :param longitude: The width of the canvas where stars will be placed.
    :param number: The number of stars to generate.
    :return: Yields tuples (y_axis, x_axis, symbol) for each generated star.
    """
    for _ in range(number):
        y_axis = random.randint(1, latitude - 2)
        x_axis = random.randint(1, longitude - 2)
        element = random.choice(ELEMENTS)
        yield y_axis, x_axis, element


def draw_stars(canvas, height, width):
    """
    Create and display stars on the canvas.

    This function generates a specified number of stars
    at random positions on the canvas.
    Each star is created using the 'blink' function,
    which animates the stars to make them twinkle.
    The positions and symbols of the stars are generated
    by the 'create_stars' function.

    :param canvas: The curses canvas on which the stars will be displayed.
    :param height: The height of the canvas,
    used to determine the range of possible star positions.
    :param width: The width of the canvas,
    used to determine the range of possible star positions.
    """
    stars = [
        blink(canvas, y_axis, x_axis, symbol, random.randint(0, 3))
        for y_axis, x_axis, symbol in create_stars(height, width)
    ]

    for star in stars:
        variables.garbage_coroutines.append(star)


def draw_window(canvas, height):
    """
    Create and display a status window at the bottom of the main canvas.

    This function creates a sub-window (status window)
    at the bottom of the main canvas.
    The status window is used to display text
    or information related to the game's status.
    It defines the size and position of the status window
    and initializes it with a border and text.

    :param canvas: The main curses canvas where
    the status window will be displayed.
    :param height: The height of the main canvas,
    used to determine the position of the status window.
    """
    # Determine the dimensions of the sub-window
    status_window_height = 3
    status_window_width = 60

    # Position the sub-window at the bottom left corner
    status_window_y = height - status_window_height
    status_window_x = 0

    # Create the sub-window
    status_window = canvas.derwin(
        status_window_height,
        status_window_width,
        status_window_y,
        status_window_x
    )
    status_window.box()
    status_window.addstr(
        1, (status_window_width - len(variables.text)) // 2, variables.text
    )
    status_window.refresh()


def draw(canvas):
    """
    Main drawing function for the game.

    :param canvas: Main canvas of the game where elements are drawn.
    """
    curses.curs_set(False)
    canvas.nodelay(True)
    height, width = canvas.getmaxyx()
    draw_stars(canvas, height, width)
    variables.garbage_coroutines.append(show_phrases(canvas, phase=TIME_PHASE))
    variables.garbage_coroutines.append(
        animate_spaceship(canvas, height, width)
    )
    variables.garbage_coroutines.append(fill_orbit_with_garbage(canvas, width))
    while True:
        for value in variables.garbage_coroutines[:]:
            try:
                value.send(None)
            except StopIteration:
                variables.garbage_coroutines.remove(value)
            except Exception as e:
                logging.error(
                    f"Error inside while of draw function: {e}",
                    exc_info=True
                )
        canvas.border()
        canvas.refresh()
        # Перерисовка рамки подокна
        draw_window(canvas, height)
        curses.napms(int(TIC_TIMEOUT * 1000))


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
