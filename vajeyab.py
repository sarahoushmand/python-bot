import requests
import json
from decouple import config
import os


# os.environ['https_proxy'] = 'socks5h://127.0.0.1:1050/'
# os.environ['HTTPS_PROXY'] = 'socks5h://127.0.0.1:1050/'

TOKEN = config('TOKEN')
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates():
    url = URL + "getUpdates"
    js = get_json_from_url(url)
    return js


def process_word(updates, index):
    last_update = len(updates["result"]) - 1
    if last_update != index:
        result = search_vajeyab(updates["result"][last_update]["message"]["text"])
        chat_id = updates["result"][last_update]["message"]["chat"]["id"]
        send_message(result, chat_id)


def search_vajeyab(text):
    url = "http://api.vajehyab.com/v3/search"
    params = {'q': text, 'type': 'exact', 'token': '76559.0i2SwkzOJkdMENCpR4I9Td59D81pugRuzUm6eVUX'}
    response = requests.get(url, params=params)
    res = json.loads(response.text)
    if not res['data']['results']:
        result = 'متاسفانه واٰژه وجود ندارد'
    else:
        result = res['data']['results'][1]['text']
    return result


def send_message(text1, chat_id):
    url = URL + "sendMessage?text={}&chat_id={}".format(text1, chat_id)
    get_url(url)


message_index = 0
while True:
    bot = get_updates()
    process_word(bot, message_index)
    message_index = len(bot['result']) - 1

