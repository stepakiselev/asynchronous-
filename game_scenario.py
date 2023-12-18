import logging
import variables
from space_garbage import wait

# Logging configuration
logging.basicConfig(
    filename='app.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

PHRASES = {
    # Только на английском, Repl.it ломается на кириллице
    1957: "First Sputnik",
    1961: "Gagarin flew!",
    1969: "Armstrong got on the moon!",
    1971: "First orbital space station Salute-1",
    1981: "Flight of the Shuttle Columbia",
    1998: "ISS start building",
    2011: "Messenger launch to Mercury",
    2020: "Take the plasma gun! Shoot the garbage!",
}

async def show_phrases(canvas, status_window, status_window_width, phase):
    """
    Display changing phrases in the status window.

    :param canvas: Canvas for drawing.
    :param status_window: Window where the status will be shown.
    :param status_window_width: Width of the status window.
    :param phase: Delay between changing phrases.
    """
    try:
        for year, text in PHRASES.items():
            # Updating global variable 'year' to reflect current phrase's year
            variables.year = year
            status_text = f"{year}: {text}"
            # Adjusting the text to fit in the status window
            if len(status_text) > status_window_width - 2:
                status_text = status_text[:status_window_width - 8] + '...'
            # Updating global variable 'text' to hold the current status text
            variables.text = status_text
            await wait(phase)
    except Exception as e:
        logging.error(f"Error in show_phrases function: {e}", exc_info=True)
