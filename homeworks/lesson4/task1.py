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

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'}

news = []
dates = []
str_now = str(datetime.datetime.now())
client = MongoClient('127.0.0.1', 27017)
db = client['news2021']
db_news = db.news

# db_news.delete_many({})
# db_news.create_Index({"href": 1}, {"unique": True})


"""----------------------Собираем новости c news.mail.ru----------------------------"""

url = 'https://news.mail.ru'
response = requests.get(url, headers=header)

dom = html.fromstring(response.text)

items = dom.xpath("//li//a|"
                  "//span[contains(@class,'cell')]/a[contains(@class,'newsitem')]|"
                  "//div[contains(@class,'daynews')]/a")


for item in items:
    new = {}
    new['href'] = " ".join(item.xpath("./@href"))

    url_in = new['href']
    response_in = requests.get(url_in, headers=header)
    dom_in = html.fromstring(response_in.text)

    new['dt'] = " ".join(dom_in.xpath("//div[@class='breadcrumbs breadcrumbs_article js-ago-wrapper']//@datetime"))
    new['name'] = " ".join(dom_in.xpath("//h1[@class='hdr__inner']/text()"))
    new['resource'] = " ".join(dom_in.xpath(
        "//div[@class='breadcrumbs breadcrumbs_article js-ago-wrapper']//span[@class='link__text']/text()"))

    try:
        db_news.insert_one(new)
    except:
        pass

"""---------------------Собираем новости с lenta.ru из секции топ----------------------------"""

url = 'https://lenta.ru'
response = requests.get(url, headers=header)

dom = html.fromstring(response.text)

items = dom.xpath(
    "//section[@class='row b-top7-for-main js-top-seven']//div[@class='item']|"
    "//section[@class='row b-top7-for-main js-top-seven']//h2")

for item in items:
    new = {}
    new['resource'] = url
    new['name'] = " ".join(item.xpath(".//text()")).replace(' ', ' ')[6:]
    new['href'] = url + " ".join(item.xpath(".//@href"))
    new['dt'] = " ".join(item.xpath(".//@datetime"))
    try:
        db_news.insert_one(new)
    except:
        pass

"""-------------------Собираем новости с yandex-новости----------------------------"""

url = 'https://yandex.ru/news/'
response = requests.get(url, headers=header)

dom = html.fromstring(response.text)

items = dom.xpath("//article[contains(@class,'mg-card')]")

for item in items:
    new = {}
    new['resource'] = " ".join(item.xpath(".//@aria-label"))[10:]
    new['name'] = " ".join(item.xpath(".//h2[@class='mg-card__title']/text()")).replace(' ', ' ')
    new['href'] = " ".join(item.xpath(".//div/a/@href"))
    new['dt'] = " ".join(item.xpath(".//span[@class='mg-card-source__time']//text()"))
    if new['dt'].count('вчера в') > 0:
        new['dt'] = str(datetime.date.today() - datetime.timedelta(days=1)) + new['dt'][7:]
    else:
        new['dt'] = str(datetime.date.today()) + ' ' + new['dt']
    try:
        db_news.insert_one(new)
    except:
        pass

for new in db_news.find({}, {'_id': False}):
    pprint(new)
