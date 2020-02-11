# -*- coding: utf-8 -*-
import requests
import json
import pprint

import io
from urllib2 import urlopen

class WeatherInfo:
    def __init__(self, date, image):
      self.date = date
      self.image = image
    
    # def date(self):
    #     return self.date

    # def image(self):
    #     return self.image

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
        image = image_file
        # image = pg.image.load(image_file)
        return image

def get_weathers():
    url = 'http://weather.livedoor.com/forecast/webservice/json/v1?city=260010'
    
    response = requests.get(url)
    # print(response.status_code)
    # print(response.text)
    
    response_hash = json.loads(response.text)
    
    indexes = list(range(0, 3))

    def get_weather(index):
       forecast = response_hash['forecasts'][index]
       if (forecast['image'] is None):
           image = None
       else :
           image_url = forecast['image']['url']
           # image_str = urlopen(image_url).read()
           # image_file = io.BytesIO(image_str)
           # image = image_file
           # image = pg.image.load(image_file)
           image = weather_image_repo.get_image(image_url)

       return WeatherInfo(forecast['dateLabel'], image)
       # return "%s %s" % (forecast['dateLabel'], forecast['telop'])

    labels = list(map(get_weather, indexes))
    return labels




# print(u'あいう')


weather_image_repo = WeatherImageRepository()
weathers = get_weathers()
for w in weathers:
    print(w.date, w.image)



# 日本語コメント

