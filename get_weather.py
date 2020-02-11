# -*- coding: utf-8 -*-
import requests
import json
import pprint


def get_weathers():
    url = 'http://weather.livedoor.com/forecast/webservice/json/v1?city=260010'
    
    response = requests.get(url)
    # print(response.status_code)
    # print(response.text)
    
    response_hash = json.loads(response.text)
    
    indexes = list(range(0, 3))

    def get_weather_label(index):
       forecast = response_hash['forecasts'][index]
       return "%s %s" % (forecast['dateLabel'], forecast['telop'])

    labels = list(map(get_weather_label, indexes))
    return labels




# print(u'あいう')


weathers = get_weathers()
for w in weathers:
    print(w)



# 日本語コメント

