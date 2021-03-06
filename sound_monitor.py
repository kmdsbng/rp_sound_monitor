# -*- coding:utf-8 -*-
import numpy as np
import pyaudio
import pygame
from pygame.locals import *
import datetime
import os
import subprocess
import requests
import json
import pprint
import io
from urllib2 import urlopen
import re

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
MEDIUM_FONT = pygame.font.SysFont("notosansmonocjkjp", 50)
MEDIUM2_FONT = pygame.font.SysFont("notosansmonocjkjp", 30)
KINENBI_FONT = pygame.font.SysFont("notosansmonocjkjp", 32)

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


def each_slice(arr, n):
    return [arr[i:i + n] for i in range(0, len(arr), n)]


class ScreenRenderer:
    def __init__(self, screen, back_ground_color, alert_count, text_color, in_night, sound_logs, now, weathers, kinenbi_str):
        self.screen = screen
        self.back_ground_color = back_ground_color
        self.alert_count = alert_count
        self.text_color = text_color
        self.in_night = in_night
        self.sound_logs = sound_logs
        self.now = now
        self.weathers = weathers
        self.kinenbi_str = kinenbi_str

    def get_kinenbi_strs(self):
        return each_slice(self.kinenbi_str, 14)

    def render(self):
        self.screen.fill(self.back_ground_color)


        time_text = MEDIUM_FONT.render("%d/%d %d:%02d" % (self.now.month, self.now.day, self.now.hour, self.now.minute), True, self.text_color)
        screen.blit(time_text, [480, 0])

        alert_count_text = MEDIUM_FONT.render("%d" % (self.alert_count), True, self.text_color)
        screen.blit(alert_count_text, [480, 60])


        for i, w in enumerate(self.weathers):
            weather_text = MEDIUM2_FONT.render(w.date, True, self.text_color)
            screen.blit(weather_text, [480, 120 + i * 70])
            screen.blit(w.image, [570, 120 + i * 70])
            temp_text = MEDIUM2_FONT.render(w.temp_str(), True, self.text_color)
            screen.blit(temp_text, [670, 120 + i * 70])

        # jp_text = MEDIUM_FONT.render(u"aあいう", True, self.text_color)
        # screen.blit(jp_text, [500, 150])

        if self.in_night:
            night_str = "n"
        else:
            night_str = "d"

        night_text = SMALL_FONT.render(night_str, True, self.text_color)
        screen.blit(night_text, [700, 450])


        max_log_count = 200
        x_offset = 480
        max_x = 300
        virtual_max_x = 600

        pygame.draw.line(self.screen, RED, [x_offset, 400 - ALERT_THRESHOLD / 8], [x_offset + 300, 400 - ALERT_THRESHOLD / 8], 1)
        pygame.draw.line(self.screen, GRAY, [x_offset, 476], [x_offset + 300, 476], 1)

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
            x = x_offset + x * max_x / virtual_max_x
            pygame.draw.line(screen, graph_color, [x, 475], [x, 475 - sound / 8], width)

        kinenbi_strs = self.get_kinenbi_strs()
        for i, str in enumerate(kinenbi_strs):
            kinenbi_text = KINENBI_FONT.render(str, True, self.text_color)
            screen.blit(kinenbi_text, [5, 5 + 32 * i])


# def get_weathers():
#     url = 'http://weather.livedoor.com/forecast/webservice/json/v1?city=260010'
#     
#     response = requests.get(url)
#     # print(response.status_code)
#     # print(response.text)
#     
#     response_hash = json.loads(response.text)
#     
#     indexes = list(range(0, 3))
# 
#     def get_weather_label(index):
#        forecast = response_hash['forecasts'][index]
#        return "%s %s" % (forecast['dateLabel'], forecast['telop'])
# 
#     labels = list(map(get_weather_label, indexes))
#     return labels

class WeatherInfo:
    def __init__(self, date, telop, image, min_temp, max_temp):
      self.date = date
      self.telop = telop
      self.image = image
      self.min_temp = min_temp
      self.max_temp = max_temp

    def temp_str(self):
        if self.min_temp != "" or self.max_temp != "":
            return u"%s〜%s℃" % (self.min_temp, self.max_temp)
        else :
            return ""
    

class WeatherImageRepository:
    def __init__(self):
        self.image_dic = {}

    def get_image(self, url):
        if url not in self.image_dic:
            self.image_dic[url] = self.load_image(url)

        return self.image_dic[url]

    def load_image(self, url):
        image_str = urlopen(url).read()
        image_file = io.BytesIO(image_str)
        #image = image_file
        image = pygame.image.load(image_file)
        rect = image.get_rect()
        image = pygame.transform.scale(image, (rect.width * 2, rect.height * 2))
        return image

def get_weathers():
    url = 'http://weather.livedoor.com/forecast/webservice/json/v1?city=260010'
    
    response = requests.get(url)
    # print(response.status_code)
    # print(response.text)
    
    response_hash = json.loads(response.text)
    size = len(response_hash['forecasts'])
    indexes = list(range(0, size))

    def get_weather(index):
       forecast = response_hash['forecasts'][index]
       if 'image' not in forecast:
           image = None
       else :
           image_url = forecast['image']['url']
           image = weather_image_repo.get_image(image_url)

       temperature = forecast['temperature']
       if temperature['min'] is None:
           min_temp = ''
       else :
           min_temp = temperature['min']['celsius']
     
       if temperature['max'] is None:
           max_temp = ''
       else :
           max_temp = temperature['max']['celsius']

       return WeatherInfo(forecast['dateLabel'], forecast['telop'], image, min_temp, max_temp)

    weathers = list(map(get_weather, indexes))
    return weathers



# print(u'あいう')

def load_kinenbi_json():
    path = '../kinenbi_data/kinenbi.json'
    f = open(path, 'r')

    json_data = json.load(f)
    return json_data


def get_kinenbi(kinenbi_json, date):
    date_key = "%02d%02d" % (date.month, date.day)

    if (date_key in kinenbi_json):
        title = kinenbi_json[date_key]['title']
        desc = re.sub(u'[\r\n 　\t]', '', kinenbi_json[date_key]['description'])
        return u"%s　　%s" % (title, desc)
    else:
        return ""



def main(kinenbi_json):
    alert_count = 0
    sound_logs =[]
    carryOn = True
    alert_count_date = datetime.date.today()

    weathers = get_weathers()
    last_hour = -1 

    while carryOn:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                carryOn = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.display.set_mode(size)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
            pygame.display.set_mode(size, FULLSCREEN)

        now = datetime.datetime.now()
        kinenbi_str = get_kinenbi(kinenbi_json, datetime.date.today())
        in_night = is_night_time(now)

        back_ground_color = BLACK
        max_sound = 0
        for sound in sound_logs:
            if max_sound < sound:
                max_sound = sound

        text_color = WHITE
        if max_sound > ALERT_THRESHOLD:
            back_ground_color = BACK_GROUND_RED

        # if alert_count > 0:
        #     text_color = TEXT_RED


        screen_renderer = ScreenRenderer(screen, back_ground_color, alert_count, text_color, in_night, sound_logs, now, weathers, kinenbi_str)
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
        color = END_TEXT
        max = np_data.max()
        min = np_data.min()

        if in_night:
          max *= 1.7 

        if max > ALERT_THRESHOLD:
            #color = RED_TEXT
            alert_count += 1
            subprocess.call(pixela_command, shell=True)
        #elif max > 200:
            #color = YELLOW_TEXT
        #elif max > 100:
            #color = CYAN_TEXT
      
        sound_logs = sound_logs + [max]
        if len(sound_logs) > 200:
            sound_logs.pop(0)
        print(color + '{0}, {1}'.format(min, max) + END_TEXT)

        if alert_count_date != datetime.date.today():
            alert_count = 0
            alert_count_date = datetime.date.today()

        if last_hour != now.hour:
            last_hour = now.hour
            weathers = get_weathers()

kinenbi_json = load_kinenbi_json()
weather_image_repo = WeatherImageRepository()
main(kinenbi_json)

pygame.quit()

stream.stop_stream()
stream.close()
audio.terminate()

print("Finish Streaming")

