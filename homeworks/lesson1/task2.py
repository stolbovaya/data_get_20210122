"""2. Изучить список открытых API (https://www.programmableweb.com/category/all/apis).
Найти среди них любое, требующее авторизацию (любого типа).
Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл."""
import json
import requests

oauth_token = "AgAAAAAHdzZpAATuwcBgXrs4f0bfj-CcD2EIadA"


def create_token(in_oauth_token) -> object:
    f_params = {'yandexPassportOauthToken': in_oauth_token}
    f_response = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens', params=f_params)
    decode_response = f_response.content.decode('UTF-8')
    text = json.loads(decode_response)
    iam_token = text.get('iamToken')

    return iam_token


IAM_oauth_token = create_token(oauth_token.format(oauth_token))

print(f'Токен успешно сгенерирован {IAM_oauth_token} ')

params = {'folder_id': 'b1gdcsv1e916eerpiba3',
          'texts': ['Hello', 'World'], 'targetLanguageCode': 'ru'}

headers = {'Authorization': 'Bearer ' + IAM_oauth_token}

response = requests.post('https://translate.api.cloud.yandex.net/translate/v2/translate', headers=headers,
                         params=params)

data = response.json()
with open('response_token.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=2, ensure_ascii=False)

