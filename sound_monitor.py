# -*- coding:utf-8 -*-
import numpy as np
import pyaudio
import pygame
from pygame.locals import *
import datetime
import os
import subprocess

pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
CYAN = (128, 255, 0)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
BACK_GROUND_RED = (200, 0, 0)
TEXT_RED = (255, 160, 160)

ALERT_THRESHOLD = 500

CHUNK=1024
RATE=16000
audio=pyaudio.PyAudio()

BLACK_TEXT='\033[30m'
RED_TEXT='\033[31m'
YELLOW_TEXT='\033[33m'
CYAN_TEXT='\033[36m'
END_TEXT='\033[0m'

# MEDIUM_FONT = pygame.font.Font(None, 60)
SMALL_FONT = pygame.font.Font(None, 20)
MEDIUM_FONT = pygame.font.SysFont("notosansmonocjkjp", 60)

pixela_token = os.environ['PIXELA_TOKEN']
pixela_command = "curl -X PUT https://pixe.la/v1/users/kmdsbng/graphs/soundalert/increment -H 'X-USER-TOKEN:%s'" % (pixela_token)

def is_night_time(target_time):
    hour = target_time.hour
    if hour >= 20 or hour <= 6:
      return True
    else:
      return False

stream = audio.open(  format = pyaudio.paInt16,
        channels = 1,
        rate = RATE,
        frames_per_buffer = CHUNK,
        input = True )

size = (800, 480)
screen = pygame.display.set_mode(size, FULLSCREEN)
pygame.display.set_caption("Sound Monitor")

carryOn = True

clock = pygame.time.Clock()



class ScreenRenderer:
    def __init__(self, screen, back_ground_color, alert_count, text_color, in_night, sound_logs, now):
        self.screen = screen
        self.back_ground_color = back_ground_color
        self.alert_count = alert_count
        self.text_color = text_color
        self.in_night = in_night
        self.sound_logs = sound_logs
        self.now = now

    def render(self):
        self.screen.fill(self.back_ground_color)

        pygame.draw.line(self.screen, RED, [0, 400 - ALERT_THRESHOLD / 2], [600, 400 - ALERT_THRESHOLD / 2], 1)
        pygame.draw.line(self.screen, GRAY, [0, 401], [600, 401], 1)

        alert_count_text = MEDIUM_FONT.render("%d" % (self.alert_count), True, self.text_color)
        screen.blit(alert_count_text, [605, 100])

        time_text = MEDIUM_FONT.render("%d/%d %d:%d" % (self.now.month, self.now.day, self.now.hour, self.now.minute), True, self.text_color)
        screen.blit(time_text, [500, 0])

        # jp_text = MEDIUM_FONT.render(u"aあいう", True, self.text_color)
        # screen.blit(jp_text, [500, 150])

        if self.in_night:
            night_str = "n"
        else:
            night_str = "d"

        night_text = SMALL_FONT.render(night_str, True, self.text_color)
        screen.blit(night_text, [700, 450])

        for index, sound in enumerate(self.sound_logs):
            graph_color = GREEN
            width = 3
            if sound > ALERT_THRESHOLD:
                graph_color = WHITE
                width = 30
            elif sound > 200:
                graph_color = YELLOW
                width = 10
            elif sound > 100:
                graph_color = CYAN
                width = 5

            sound_logs_len = len(self.sound_logs)
            x = (sound_logs_len - index) * 3
            pygame.draw.line(screen, graph_color, [x, 400], [x, 400 - sound / 2], width)


def main():
    alert_count = 0
    sound_logs =[]
    carryOn = True
    alert_count_date = datetime.date.today()

    while carryOn:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                carryOn = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.display.set_mode(size)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
            pygame.display.set_mode(size, FULLSCREEN)

        now = datetime.datetime.now()
        in_night = is_night_time(now)

        back_ground_color = BLACK
        max_sound = 0
        for sound in sound_logs:
            if max_sound < sound:
                max_sound = sound

        text_color = WHITE
        if max_sound > ALERT_THRESHOLD:
            back_ground_color = BACK_GROUND_RED

        if alert_count > 0:
            text_color = TEXT_RED


        screen_renderer = ScreenRenderer(screen, back_ground_color, alert_count, text_color, in_night, sound_logs, now)
        screen_renderer.render()


        #alert_count_text = font.render("ALERT", True, text_color)
        #screen.blit(alert_count_text, [605, 100])


      
        pygame.display.flip()
      
        inputs = []
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

        if in_night:
          max *= 2

        if max > ALERT_THRESHOLD:
            color = RED_TEXT
            alert_count += 1
            subprocess.call(pixela_command, shell=True)
        elif max > 200:
            color = YELLOW_TEXT
        elif max > 100:
            color = CYAN_TEXT
      
        sound_logs = sound_logs + [max]
        if len(sound_logs) > 200:
            sound_logs.pop(0)
        print(color + '{0}, {1}'.format(min, max) + END_TEXT)

        if alert_count_date != datetime.date.today():
            alert_count = 0
            alert_count_date = datetime.date.today()

main()

pygame.quit()

stream.stop_stream()
stream.close()
audio.terminate()

print("Finish Streaming")

