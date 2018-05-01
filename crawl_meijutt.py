#-*- coding:utf-8 -*-

import requests
from bs4 import BeautifulSoup

import os

base_url = "http://www.meijutt.com"

def search_series(name):
    name = name.decode("utf8").encode("gb2312")
    r = requests.post(base_url+"/search.asp", data = {'searchword':name})
    r.encoding = "gb2312"
    soup = BeautifulSoup(r.text, "html.parser")
    results = soup.find_all(class_="bor_img3_right")
    for result in results:
        href = result.a
        print href['href']
        print href['title']

def get_series_detail(detail_url):
    r = requests.get(base_url + detail_url)
    r.encoding = "gb2312"
    soup = BeautifulSoup(r.text, "html.parser")
    results = soup.find_all(class_="down_url")
    for result in results:
        print result['file_name']
        print result['value']


search_series("邪恶力量")
get_series_detail("/content/meiju23086.html")

