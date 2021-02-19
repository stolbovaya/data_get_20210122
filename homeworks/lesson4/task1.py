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
import datetime


def get_datetime(fdates, href, fnow):
    for fdt_item in fdates:
        try:
            if fdt_item.get('hrefs').index(href) > -1:
                return fdt_item.get('datetime')

        except ValueError:
            pass
    return fnow


header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'}

url = 'https://news.mail.ru'
response = requests.get(url, headers=header)

dom = html.fromstring(response.text)
news = []
dates = []
str_now = str(datetime.datetime.now())
client = MongoClient('127.0.0.1', 27017)
db = client['news2021']
db_news = db.news

# db_news.delete_many({})
# db_news.create_Index({"href": 1}, {"unique": True})

items = dom.xpath("//div[@class='cols__inner']")

for item in items:
    dt = {}
    dt['datetime'] = " ".join(item.xpath('.//span[@datetime]/@datetime'))
    dt['hrefs'] = item.xpath('.//@href')

    dates.append(dt)

pprint(dates)

"""Собираем текстовые новости"""

items = dom.xpath("//a[@class='list__text']|//a[@class='link link_flex']|//a[@class='newsitem__title link-holder']")

for item in items:
    new = {}
    new['resource'] = url
    new['name'] = " ".join(item.xpath(".//text()")).replace(' ', ' ').replace('\r', '').replace('\n', '').replace("'",
                                                                                                                  '')
    new['href'] = " ".join(item.xpath(".//@href"))

    new['dt'] = get_datetime(dates, new['href'], str_now)

    try:
        db_news.insert_one(new)
    except:
        pass

"""Собираем новости с фотографиями"""

items = dom.xpath(
    '//a[@class="photo photo_full photo_scale js-topnews__item"]|//a[@class="photo photo_small photo_scale photo_full js-topnews__item"]|//a[@class="photo photo_small photo_full photo_scale js-show_photo"]')

for item in items:
    new = {}
    new['resource'] = url
    new['name'] = " ".join(item.xpath(".//span[contains(@class,'photo__title')]//text()")).replace(' ', ' ')
    new['href'] = item.xpath(".//@href")
    new['dt'] = get_datetime(dates, new['href'], str_now)
    try:
        db_news.insert_one(new)
    except:
        pass


"""Собираем новости с https://lenta.ru из секции топ"""
url = 'https://lenta.ru'
response = requests.get(url, headers=header)

dom = html.fromstring(response.text)

items = dom.xpath("//section[@class='row b-top7-for-main js-top-seven']//div[@class='item']")

for item in items:
    new = {}
    new['resource'] = url
    new['name'] = " ".join(item.xpath(".//text()")).replace(' ', ' ')
    new['href'] = url+" ".join(item.xpath(".//@href"))
    new['dt'] = " ".join(item.xpath(".//@datetime"))
    try:
        db_news.insert_one(new)
    except:
        pass


for new in db_news.find({}, {'_id': False}):
    pprint(new)
