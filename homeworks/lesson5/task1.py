"""1) Написать программу, которая собирает входящие письма из своего или тестового почтового ящика
и сложить данные о письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)
Логин тестового ящика: study.ai_172@mail.ru
Пароль тестового ящика: NextPassword172
"""
import time
from pprint import pprint

from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def get_letter(driver_in):
    rez = {}

    rez['email_subject'] = WebDriverWait(driver_in, 20).until(
        EC.presence_of_element_located((By.XPATH, "//div[@class='thread__header']//h2"))).text

    rez['email_date'] = driver_in.find_element_by_class_name("letter__date").text

    email_from = driver_in.find_element_by_xpath("//div[@class='letter__author']").find_element_by_tag_name('span')
    rez['email_from'] = email_from.get_attribute('title')

    body = driver_in.find_elements_by_xpath("//div[@class='letter-body']//div[@class='html-parser']")
    email_body = []
    for el in body:
        email_body.append(el.text.replace('\n', ''))
    rez['email_body'] = ' '.join(email_body)

    return rez


def authorization_mail_ru(username, password):
    driver = webdriver.Chrome()

    driver.get('https://account.mail.ru')

    elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'username')))
    elem.send_keys(username)
    elem.send_keys(Keys.ENTER)
    elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'password')))
    elem.send_keys(password)
    elem.send_keys(Keys.ENTER)
    return driver



driver = authorization_mail_ru("study.ai_172@mail.ru", "NextPassword172")

#-----------Ждем загрузку страницы-------------------------------------
el = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CLASS_NAME, "application-mail")))
el = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CLASS_NAME, "llc")))
#----------------------------------------------------------------------
letters_href = set()
last_el = ''

while True:

    letters_el = driver.find_elements_by_class_name("js-letter-list-item")
    for el in letters_el:
        letters_href.add(el.get_attribute('href'))
    cur_el = letters_el[-1].get_attribute('href')
    letters_el[-1].send_keys(Keys.PAGE_DOWN)

    if last_el == cur_el:
        break
    last_el = cur_el
    time.sleep(3)

pprint(len(letters_href))
letters = []


for el in letters_href:
    driver.get(el)
    letters.append(get_letter(driver))

driver.close()

client = MongoClient('127.0.0.1', 27017)
db = client['mail_2021']
db_mail = db.mail
db_mail.insert_many(letters)

for mail in db_mail.find({}, {'_id': False}):
    pprint(mail)



