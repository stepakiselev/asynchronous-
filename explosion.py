import asyncio
import curses
import logging
from frame import draw_frame, get_frame_size


logging.basicConfig(
    filename='app.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

EXPLOSION_FRAMES = [
    """\
           (_)
       (  (   (  (
      () (  (  )
        ( )  ()
    """,
    """\
           (_)
       (  (   (
         (  (  )
          )  (
    """,
    """\
            (
          (   (
         (     (
          )  (
    """,
    """\
            (
              (
            (
    """,
]


async def explode(canvas, center_row, center_column):
    """
    Animate an explosion at a specified location on the canvas.

    This function creates an explosion animation using predefined frames.
    It displays each frame of the explosion
    at the specified center coordinates.
    Before starting the animation,
    it checks if the explosion frames are available.
    The function also triggers a beep sound to accompany the visual effect.

    :param canvas: The curses canvas where the explosion will be animated.
    :param center_row: The row coordinate of the explosion's center
    on the canvas.
    :param center_column: The column coordinate of the explosion's
    center on the canvas.
    """
    if not EXPLOSION_FRAMES[0]:
        logging.error("EXPLOSION_FRAMES is empty.")

    rows, columns = get_frame_size(EXPLOSION_FRAMES[0])
    corner_row = center_row - rows / 2
    corner_column = center_column - columns / 2

    curses.beep()
    for frame in EXPLOSION_FRAMES:

        draw_frame(canvas, corner_row, corner_column, frame)

        await asyncio.sleep(0)
        draw_frame(canvas, corner_row, corner_column, frame, negative=True)
        await asyncio.sleep(0)
