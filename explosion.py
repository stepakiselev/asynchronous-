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
    if not EXPLOSION_FRAMES[0]:
        logging.error(f"EXPLOSION_FRAMES is empty.")
    rows, columns = get_frame_size(EXPLOSION_FRAMES[0])
    corner_row = center_row - rows / 2
    corner_column = center_column - columns / 2

    curses.beep()
    try:
        for frame in EXPLOSION_FRAMES:

            draw_frame(canvas, corner_row, corner_column, frame)

            await asyncio.sleep(0)
            draw_frame(canvas, corner_row, corner_column, frame, negative=True)
            await asyncio.sleep(0)
    except Exception as e:
        logging.error(f"Error in explode function: {e}", exc_info=True)
