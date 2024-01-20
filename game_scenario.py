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


async def show_phrases(phase):
    """
    Display changing phrases in the status window.

    :param phase: Delay between changing phrases.
    """
    for year, text in PHRASES.items():
        # Updating global variable 'year' to reflect current phrase's year
        variables.year = year
        status_text = f"{year}: {text}"
        variables.text = status_text
        await wait(phase)
