"""2) Написать программу, которая собирает «Хиты продаж» с сайта техники mvideo и складывает данные в БД.
Магазины можно выбрать свои. Главный критерий выбора: динамически загружаемые товары"""
import json
import time
from pprint import pprint

from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()

driver.get('https://www.mvideo.ru/')

hit_elem = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located(
        (By.XPATH, "//div[@class='section']//div[contains(text(),'Хиты продаж')][1]/ancestor::div[3]")))

bt = hit_elem.find_element_by_xpath(
    "//a[contains(@class,'next-btn c-btn c-btn_scroll-horizontal c-btn_icon i-icon-fl-arrow-right')]")
ln_bf = 0
while True:
    goods = hit_elem.find_elements_by_class_name("gallery-list-item")
    ln = len(goods)
    if ln == ln_bf:
        break
    ln_bf = ln
    bt.click()
    time.sleep(5)

print(ln)
goods_hit = []
for good in goods:
    good_el = good.find_element_by_class_name("fl-product-tile-title__link")
    good_info = good_el.get_attribute('data-product-info')
    goods_hit.append(json.loads(good_info.replace('\n', '').replace('\t', '')))

driver.close()

client = MongoClient('127.0.0.1', 27017)
db = client['mvideo_2021']
db_goods = db.goods
db_goods.insert_many(goods_hit)

for good in db_goods.find({}, {'_id': False}):
    pprint(good)
