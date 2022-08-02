import time
import curses
import asyncio
import random

TIC_TIMEOUT = 0.1
ELEMENTS = ["+", "*", ".", ":"]

async def go_to_sleep(seconds):
    iteration_count = int(seconds * 10)
    for _ in range(iteration_count):
        await asyncio.sleep(0)
      
async def blink(canvas, row, column, symbol, sequence=1):
    while True:
      if sequence == 0:     
          canvas.addstr(row, column, symbol, curses.A_DIM)
          await go_to_sleep(2)
          sequence += 1

      if sequence == 1:
          canvas.addstr(row, column, symbol)
          await go_to_sleep(0.3)
          sequence += 1

      if sequence == 2:
          canvas.addstr(row, column, symbol, curses.A_BOLD)
          await go_to_sleep(0.5)
          sequence += 1

      if sequence == 3:
          canvas.addstr(row, column, symbol)
          await go_to_sleep(0.3)
          sequence = 0

      
def create_stars(latitude, longitude, number=50):
  for star in range(number):
    axis_y = random.randint(1, latitude - 1)
    axis_x = random.randint(1, longitude - 1)
    element = random.choice(ELEMENTS)
    yield axis_y, axis_x, element

def draw(canvas):
  curses.curs_set(False)
  canvas.border()
  
  height, width = canvas.getmaxyx()
  
  stars = [
    blink(canvas, row, column, symbol, random.randint(0, 3)) 
    for row, column, symbol in create_stars(height, width)
  ]
  while True:
    index = 0
    while index < len(stars):
      star = stars[index]
      try:
        star.send(None)
      except StopIteration:
        stars.remove(star)
      index += 1
      
    canvas.refresh()
    time.sleep(TIC_TIMEOUT)
    
  
if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)