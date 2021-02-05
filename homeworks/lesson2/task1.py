"""Вариант 1
Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы)
с сайтов Superjob и HH.
Приложение должно анализировать несколько страниц сайта (также вводим через input или аргументы).
Получившийся список должен содержать в себе минимум:
Наименование вакансии.
Предлагаемую зарплату (отдельно минимальную и максимальную).
Ссылку на саму вакансию.
Сайт, откуда собрана вакансия.
### По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение).
Структура должна быть одинаковая для вакансий с обоих сайтов.
Общий результат можно вывести с помощью dataFrame через pandas."""

import json
import re

from bs4 import BeautifulSoup as bs
import requests


def get_salary(list_salary):
    max_salary = None
    min_salary = None
    currency = 'RUB'
    if list_salary.count('По договорённости') > 0:
        max_salary = None
        min_salary = None
    if list_salary.count('от') > 0:
        max_salary = None
        min_salary = list_salary[4].replace(' ', '').replace('руб.', '')
    if list_salary.count('до') > 0:
        max_salary = list_salary[4].replace(' ', '').replace('руб.', '')
        min_salary = None
    if list_salary.count('<span> <!-- -->—<!-- --> </span>') > 0:
        max_salary = list_salary[2].replace(' ', '').replace('руб.', '')
        min_salary = list_salary[0].replace(' ', '').replace('руб.', '')

    return {'min_salary': min_salary, 'max_salary': max_salary, 'currency': currency}


def get_salary_HH(list_salary):
    max_salary = None
    min_salary = None
    currency = 'RUB'
    if len(list_salary) > 0:
        if list_salary[0].text.find('USD') > -1:
            currency = 'USD'
        if list_salary[0].text.find('EUR') > -1:
            currency = 'EUR'
        if list_salary[0].text.find('от') > -1:
            min_salary = re.findall(r'\d+', list_salary[0].text.replace(' ', ''))[0]
        if list_salary[0].text.find('до') > -1:
            max_salary = re.findall(r'\d+', list_salary[0].text.replace(' ', ''))[0]
        if list_salary[0].text.find('-') > -1:
            f_salary = re.findall(r'\d+', list_salary[0].text.replace(' ', ''))
            min_salary = f_salary[0]
            max_salary = f_salary[1]
    return {'min_salary': min_salary, 'max_salary': max_salary, 'currency': currency}


vacances = []

bl_find = True
find_vacancy = 'Data engineer bank'

id_page = 2
url = 'https://russia.superjob.ru'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'}
my_params = {'keywords': find_vacancy}
response = requests.get(url + '/vacancy/search/', params=my_params, headers=headers)

while bl_find:
    soup = bs(response.text, 'html.parser')

    vacancy = soup.find_all('div', {'class': 'iJCa5 f-test-vacancy-item _1fma_ undefined _2nteL'})
    next_page = soup.find_all('a', {'href': '/vacancy/search/?keywords=' + find_vacancy + '&page=' + str(id_page)},
                              limit=1)

    if len(next_page) == 0:
        bl_find = False
    for vacancy_item in list(vacancy):
        vacancy_atr = list(vacancy_item.find_all('a', {'class': 'icMQ_'}))
        vacancy_location = list(vacancy_item.find_all('span', {'class': 'f-test-text-company-item-location'}))

        if len(vacancy_location) > 0:
            fs = vacancy_location[0].text.find('•')
            vacancy_location_time = vacancy_location[0].text[0:fs - 1]
            vacancy_location_place = vacancy_location[0].text[fs + 2:]
        else:
            vacancy_location_place = ''
            vacancy_location_time = ''

        if len(vacancy_atr) > 0:
            vacancy_name = vacancy_atr[0].text
            vacancy_href = url + vacancy_atr[0].attrs.get('href')
        else:
            vacancy_name = ''
            vacancy_href = ''

        if len(vacancy_atr) > 1:
            vacancy_company = vacancy_atr[1].text
        else:
            vacancy_company = ''

        vacancy_salary = get_salary(list(map(str, list(vacancy_item.find_all('span', {'class': '_3mfro'})[0]))))

        vacances.append([vacancy_name, vacancy_href, vacancy_company, vacancy_location_place, vacancy_location_time,
                         vacancy_salary])

    my_params = {'keywords': find_vacancy, 'page': str(id_page)}
    response = requests.get(url + '/vacancy/search/', params=my_params, headers=headers)
    id_page += 1

bl_find = True
id_page = 2

url = 'https://rostov.hh.ru/search/vacancy?clusters=true&enable_snippets=true&salary=&st=searchVacancy&text=' + find_vacancy.replace(
    ' ', '+')

response = requests.get(url, headers=headers)

while bl_find:
    soup = bs(response.text, 'html.parser')

    vacancy = soup.find_all('div', {'class': 'vacancy-serp-item'})
    next_page = soup.find_all('a', {
        'href': '/search/vacancy?L_is_autosearch=false&clusters=true&enable_snippets=true&text=' + find_vacancy.replace(
            ' ', '+') + '&page=' + str(id_page)}, limit=1)

    if len(next_page) == 0:
        bl_find = False
    for vacancy_item in list(vacancy):
        vacancy_atr = list(vacancy_item.find_all('a', {'class': 'bloko-link HH-LinkModifier'}))
        vacancy_company = list(vacancy_item.find_all('div', {'class': 'vacancy-serp-item__meta-info-company'}))
        vacancy_location_place = list(vacancy_item.find_all('span', {'class': 'vacancy-serp-item__meta-info'}))
        vacancy_location_time = list(
            vacancy_item.find_all('span', {'class': 'vacancy-serp-item__publication-date'}))
        vacancy_salary_list = list(vacancy_item.find_all('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}))

        if len(vacancy_location_place) > 0:
            vacancy_location_place = vacancy_location_place[0].text
        else:
            vacancy_location_place = ''

        if len(vacancy_location_time) > 0:
            vacancy_location_time = vacancy_location_time[0].text
        else:
            vacancy_location_time = ''

        if len(vacancy_atr) > 0:
            vacancy_name = vacancy_atr[0].text
            vacancy_href = vacancy_atr[0].attrs.get('href')
        else:
            vacancy_name = ''
            vacancy_href = ''

        if len(vacancy_company) > 0:
            vacancy_company = vacancy_company[0].text
        else:
            vacancy_company = ''

        vacancy_salary = get_salary_HH(vacancy_salary_list)
        vacances.append([vacancy_name, vacancy_href, vacancy_company, vacancy_location_place, vacancy_location_time,
                         vacancy_salary])

    response = requests.get(
        'https://rostov.hh.ru/search/vacancy?L_is_autosearch=false&clusters=true&enable_snippets=true&text=' + find_vacancy.replace(
            ' ', '+') + '&page=' + str(id_page), headers=headers)
    id_page += 1

print(json.dumps(vacances, indent=4, sort_keys=True, ensure_ascii=False))
