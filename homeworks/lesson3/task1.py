"""
1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, записывающую собранные вакансии в созданную БД.
2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы.
3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта."""

"""
В консоли создали индекс
db.vacancies.createIndex( { "vacancy_href": 1 }, { unique: true } )
"""

import json
import re
from bs4 import BeautifulSoup as bs
import requests

from pymongo import MongoClient
from pprint import pprint


def get_salary(list_salary):
    max_salary_int = None
    min_salary_int = None
    max_salary = None
    min_salary = None
    currency = None
    if len(list_salary) > 0:
        currency = 'RUB'
        if list_salary[0].text.find('USD') > -1:
            currency = 'USD'
        if list_salary[0].text.find('EUR') > -1:
            currency = 'EUR'
        if list_salary[0].text.find('от ') > -1:
            min_salary = re.findall(r'\d+', list_salary[0].text.replace(' ', ''))[0]
        if list_salary[0].text.find('до ') > -1:
            max_salary = re.findall(r'\d+', list_salary[0].text.replace(' ', ''))[0]
        if list_salary[0].text.find('-') > -1 or list_salary[0].text.find('—') > -1:
            f_salary = re.findall(r'\d+', list_salary[0].text.replace(' ', ''))
            min_salary = f_salary[0]
            max_salary = f_salary[1]
        try:
            min_salary_int = int(min_salary)
        except TypeError:
            pass

        try:
            max_salary_int = int(max_salary)
        except TypeError:
            pass

    return {'min_salary': min_salary_int, 'max_salary': max_salary_int, 'currency': currency}


def add_new_vacancies(vacancy):
    url = 'https://russia.superjob.ru'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'}

    my_params = {'keywords': vacancy}
    response = requests.get(url + '/vacancy/search/', params=my_params, headers=headers)
    id_page = 2
    while True:
        soup = bs(response.text, 'html.parser')
        vacancies = soup.find_all('div', {'class': 'f-test-vacancy-item'})

        for vacancy_item in list(vacancies):
            vacancy_atr = list(vacancy_item.find_all('a', {'class': 'icMQ_'}))
            vacancy_location = list(vacancy_item.find_all('span', {'class': 'f-test-text-company-item-location'}))

            if len(vacancy_location) > 0:
                fs = vacancy_location[0].text.find('•')
                vacancy_location_time = vacancy_location[0].text[0:fs - 1].replace(' ', ' ')
                vacancy_location_place = vacancy_location[0].text[fs + 2:].replace(' ', ' ')
            else:
                vacancy_location_place = None
                vacancy_location_time = None

            if len(vacancy_atr) > 0:
                vacancy_name = vacancy_atr[0].text
                vacancy_href = url + vacancy_atr[0].attrs.get('href')
            else:
                vacancy_name = None
                vacancy_href = None

            if len(vacancy_atr) > 1:
                vacancy_company = vacancy_atr[1].text
            else:
                vacancy_company = None

            vacancy_salary = get_salary(list(vacancy_item.find_all('span', {'class': '_3mfro'})))

            try:
                db_vacancies.insert_one(
                    {'vacancy_name': vacancy_name, 'vacancy_href': vacancy_href, 'vacancy_company': vacancy_company,
                     'vacancy_location_place': vacancy_location_place,
                     'vacancy_location_time': vacancy_location_time,
                     'vacancy_salary': vacancy_salary})
            except:
                pass

        if len(soup.find_all('a', {'class': 'f-test-button-dalshe'}, limit=1)) == 0:
            break

        my_href = '/vacancy/search/?keywords=' + vacancy + '&page=' + str(id_page)
        response = requests.get(url + my_href, headers=headers)
        id_page += 1

    id_page = 1
    url = 'https://rostov.hh.ru'
    my_href = '/search/vacancy?clusters=true&enable_snippets=true&salary=&st=searchVacancy&text=' + vacancy
    response = requests.get(url + my_href, headers=headers)

    while True:
        soup = bs(response.text, 'html.parser')
        vacancies = soup.find_all('div', {'class': 'vacancy-serp-item'})

        for vacancy_item in list(vacancies):
            vacancy_atr = list(vacancy_item.find_all('a', {'class': 'bloko-link HH-LinkModifier'}))
            vacancy_company = list(vacancy_item.find_all('div', {'class': 'vacancy-serp-item__meta-info-company'}))
            vacancy_location_place = list(vacancy_item.find_all('span', {'class': 'vacancy-serp-item__meta-info'}))
            vacancy_location_time = list(
                vacancy_item.find_all('span', {'class': 'vacancy-serp-item__publication-date'}))
            vacancy_salary_list = list(vacancy_item.find_all('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}))

            if len(vacancy_location_place) > 0:
                vacancy_location_place = vacancy_location_place[0].text.replace(' ', ' ')
            else:
                vacancy_location_place = ''

            if len(vacancy_location_time) > 0:
                vacancy_location_time = vacancy_location_time[0].text.replace(' ', ' ')
            else:
                vacancy_location_time = ''

            if len(vacancy_atr) > 0:
                vacancy_name = vacancy_atr[0].text
                vacancy_href = vacancy_atr[0].attrs.get('href')
            else:
                vacancy_name = ''
                vacancy_href = ''

            if len(vacancy_company) > 0:
                vacancy_company = vacancy_company[0].text.replace(' ', ' ')
            else:
                vacancy_company = ''

            vacancy_salary = get_salary(vacancy_salary_list)
            try:
                db_vacancies.insert_one(
                    {'vacancy_name': vacancy_name, 'vacancy_href': vacancy_href, 'vacancy_company': vacancy_company,
                     'vacancy_location_place': vacancy_location_place,
                     'vacancy_location_time': vacancy_location_time,
                     'vacancy_salary': vacancy_salary})
            except:
                pass

        if len(soup.find_all('a', {'class': 'bloko-button HH-Pager-Controls-Next HH-Pager-Control'}, limit=1)) == 0:
            break

        my_href = '/search/vacancy?L_is_autosearch=false&clusters=true&enable_snippets=true&text=' + vacancy + '&page=' + str(
            id_page)
        response = requests.get(url + my_href, headers=headers)
        id_page += 1


def find_vacancies(income):
    for vacancy in db_vacancies.find({'$or': [{'vacancy_salary.max_salary': {'$gt': income},
                                               'vacancy_salary.currency': {'$eq': 'RUB'}},
                                              {'vacancy_salary.max_salary': {'$gt': income / EUR},
                                               'vacancy_salary.currency': {'$eq': 'EUR'}},
                                              {'vacancy_salary.max_salary': {'$gt': income / USD},
                                               'vacancy_salary.currency': {'$eq': 'USD'}},
                                              {'vacancy_salary.max_salary': None}]},
                                     {'_id': False, 'vacancy_href': True, 'vacancy_salary': True}):
        pprint(vacancy)


USD = 73
EUR = 80
find_income = 100000
find_vacancy = 'Data engineer'

client = MongoClient('127.0.0.1', 27017)
db = client['vacancy2021']
db_vacancies = db.vacancies

# db_vacancies.delete_many({})

add_new_vacancies(find_vacancy)

find_vacancies(find_income)

# print(json.dumps(vacances, indent=4, sort_keys=True, ensure_ascii=False))
