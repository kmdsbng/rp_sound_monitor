# -*- coding: utf-8 -*-
import requests
import json
import pprint
import re
import datetime


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
        return "%s%s" % (title, desc)
    else:
        return ""


kinenbi_json = load_kinenbi_json()
today = datetime.date.today()
kinenbi_str = get_kinenbi(kinenbi_json, today)
print(kinenbi_str)



