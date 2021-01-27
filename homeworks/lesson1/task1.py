"""1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
сохранить JSON-вывод в файле *.json."""
import json
import requests

url = 'https://api.github.com'
user='stolbovaya'

response = requests.get(f'{url}/users/{user}/repos')

if response.status_code == 200:
    for i in response.json():
        print(i['name'])
    data = response.json()
    with open('response.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
else:
    print(f'Error! Status:{response.status_code}')


