"""
Написать приложение, которое собирает основные новости с сайтов news.mail.ru, lenta.ru,
yandex-новости. Для парсинга использовать XPath. Структура данных должна содержать:
название источника;
наименование новости;
ссылку на новость;
дата публикации.
Сложить собранные данные в БД
"""

import requests
from lxml import html
from pymongo import MongoClient
from pprint import pprint

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'}

url = 'https://news.mail.ru'
response = requests.get(url, headers=header)

dom = html.fromstring(response.text)

"""Собираем текстовые новости"""

items = dom.xpath("//a[@class='list__text']|//a[@class='link link_flex']|//a[@class='newsitem__title link-holder']")
news = []
for item in items:
    new = {'resource': url,
           'name': " ".join(item.xpath(".//text()")).replace(' ', ' ').replace('\r', '').replace('\n', '').replace("'",
                                                                                                                   ''),
           'href': " ".join(item.xpath(".//@href")), 'dt': None}

    news.append(new)

"""Собираем новости с фотографиями"""

items = dom.xpath(
    '//a[@class="photo photo_full photo_scale js-topnews__item"]|//a[@class="photo photo_small photo_scale photo_full js-topnews__item"]|//a[@class="photo photo_small photo_full photo_scale js-show_photo"]')
news = []
for item in items:
    new = {'resource': url, 'name': item.xpath(".//span[contains(@class,'photo__title')]//text()"),
           'href': item.xpath(".//@href"), 'dt': None}

    news.append(new)

pprint(news)

