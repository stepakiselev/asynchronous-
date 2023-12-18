import variables
from space_garbage import wait

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
    for year, text in PHRASES.items():
        variables.year = year
        status_text = f"{year}: {text}"
        if len(status_text) > status_window_width - 2:  # Учет рамки окна
            status_text = status_text[:status_window_width - 8] + '...'
        variables.text = status_text
        await wait(phase)
