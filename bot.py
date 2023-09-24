import os
import requests

from telegram import Bot
from dotenv import load_dotenv


def send_message(id, tg_token, massage):
    bot = Bot(token=tg_token)
    bot.send_message(id, massage)


def homework_status(id, tg_token, dm_token):
    timestamp = None
    params = {}
    devman_token = {'Authorization': f'Token {dm_token}'}
    url_homework_info = 'https://dvmn.org/api/long_polling/'
    negative_text = 'не принята. Кое-что нужно доработать'
    positive_text = 'принята'

    while True:
        if timestamp:
            params['timestamp'] = timestamp
        response = requests.get(url_homework_info,
                                headers=devman_token,
                                params=params)
        data = response.json()
        if 'new_attempts' in data:
            new_attempt = data['new_attempts'][0]
            is_negative = new_attempt['is_negative']
            lesson_title = new_attempt['lesson_title']
            lesson_url = new_attempt['lesson_url']
            if is_negative:
                result = negative_text
            else:
                result = positive_text
            massage = f'Работа "{lesson_title}" {result}. {lesson_url}'
            send_message(id, tg_token, massage=massage)
            timestamp = response.json()['last_attempt_timestamp']
        else:
            timestamp = response.json()['timestamp_to_request']


if __name__ == '__main__':

    load_dotenv()

    chat_id = os.environ.get('CHAT_ID')

    if not chat_id:
        chat_id = input('Ведите chat_id: ')

    tg_token = os.environ['TELEGRAM_TOKEN']
    dm_token = os.environ['DEVMAN_TOKEN']

    try:
        homework_status(chat_id, tg_token, dm_token)
    except ConnectionError as con_error:
        print(con_error)
    except requests.exceptions.ReadTimeout as rt_error:
        print(rt_error)
