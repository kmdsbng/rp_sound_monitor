# -*- coding:utf-8 -*-
import numpy as np
import pyaudio
import pygame
from pygame.locals import *

pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

size = (800, 480)
screen = pygame.display.set_mode(size, FULLSCREEN)
pygame.display.set_caption("My First Drawing")
 
carryOn = True

clock = pygame.time.Clock()

while carryOn:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            carryOn = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.display.set_mode(size)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
            pygame.display.set_mode(size, FULLSCREEN)

    
    # Game logic

    screen.fill(WHITE)
    pygame.draw.rect(screen, RED, [55, 200, 100, 70], 0)
    pygame.draw.line(screen, GREEN, [0, 0], [100, 100], 5)
    pygame.draw.ellipse(screen, BLACK, [20, 20, 250, 100], 2)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()







CHUNK=1024
RATE=16000
p=pyaudio.PyAudio()

BLACK_TEXT='\033[30m'
RED_TEXT='\033[31m'
YELLOW_TEXT='\033[33m'
CYAN_TEXT='\033[36m'
END_TEXT='\033[0m'

stream = p.open(  format = pyaudio.paInt16,
                  channels = 1,
                  rate = RATE,
                  frames_per_buffer = CHUNK,
                  input = True )

while stream.is_active():
  inputs = []
  inputs.append(stream.read(CHUNK, False))
  inputs.append(stream.read(CHUNK, False))
  inputs.append(stream.read(CHUNK, False))
  inputs.append(stream.read(CHUNK, False))
  inputs.append(stream.read(CHUNK, False))
  inputs.append(stream.read(CHUNK, False))
  inputs.append(stream.read(CHUNK, False))
  inputs.append(stream.read(CHUNK, False))
  inputs.append(stream.read(CHUNK, False))
  inputs.append(stream.read(CHUNK, False))

  input = ''.join(inputs)

  np_data = np.frombuffer(input, dtype="int16")
  #print(type(np_data))
  #print(np_data.size)
  #print(np_data.dtype)
  #print(np_data.sum())
  color = END_TEXT
  max = np_data.max()
  min = np_data.min()
  if max > 1000:
      color = RED_TEXT
  elif max > 300:
      color = YELLOW_TEXT
  elif max > 100:
      color = CYAN_TEXT

  print(color + '{0}, {1}'.format(min, max) + END_TEXT)

stream.stop_stream()
stream.close()
p.terminate()

print("Finish Streaming")

