import logging
import os


logging.basicConfig(
    filename='app.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)


def load_file(filename):
    """
    Load the content of a file.

    :param filename: Name of the file to be loaded.
    :return: Content of the file as a string.
    """
    try:
        with open(filename, "r") as frame:
            return frame.read()
    except Exception as e:
        logging.error(f"Error loading file {filename}: {e}", exc_info=True)
        return None


def get_frames(path):
    """
    Load and return a list of frames from the specified directory.

    This function reads files from the given directory
    and returns a list of their contents.
    It is primarily used for loading frame data for animations
    or graphical elements in the game.
    If the specified directory does not exist or is empty,
    an error is logged, and the function returns None.

    :param path: The path to the directory containing frame files.
    :return: A list of strings, each representing the content of a frame file.
    Returns None if the directory is missing or empty.
    """
    if not os.path.exists(path) or not os.listdir(path):
        logging.error(f"Directory '{path}' is missing or empty.")
        return  # Завершаем программу, если директория отсутствует или пуста

    list_frames = os.listdir(path=path)
    list_frame = [load_file(f"{path}{frame}") for frame in list_frames]
    return list_frame


def get_frame_size(text):
    """
    Calculate size of multiline text fragment,
    return pair — number of rows and colums.
    """
    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """
    Draw multiline text fragment on canvas,
    erase text instead of drawing if negative=True is specified.
    """
    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == ' ':
                continue

            # Check that current position it is not in
            # a lower right corner of the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)
