# -*- coding: utf-8 -*-
import requests

# http://weather.livedoor.com/weather_hacks/webservice
url = 'http://weather.livedoor.com/forecast/webservice/json/v1?city=260010'

response = requests.get(url)
print(response.status_code)
print(response.text)

# 日本語コメント

