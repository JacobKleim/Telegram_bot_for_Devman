import argparse
import os
import requests
import time

from telegram import Bot
from dotenv import load_dotenv


def get_homework_status(tg_chat_id, tg_token, dm_token, timestamp):
    params = {}
    header = {'Authorization': f'Token {dm_token}'}
    url_homework_info = 'https://dvmn.org/api/long_polling/'
    negative_text = 'не принята. Кое-что нужно доработать'
    positive_text = 'принята'
    bot = Bot(token=tg_token)
    if timestamp is not None:
        params['timestamp'] = timestamp
    response = requests.get(url_homework_info,
                            headers=header,
                            params=params)
    response.raise_for_status()
    info_checkout = response.json()
    if 'new_attempts' in info_checkout:
        new_attempt = info_checkout['new_attempts'][0]
        is_negative = new_attempt['is_negative']
        lesson_title = new_attempt['lesson_title']
        lesson_url = new_attempt['lesson_url']
        if is_negative:
            result = negative_text
        else:
            result = positive_text
        massage = f'Работа "{lesson_title}" {result}. {lesson_url}'
        bot.send_message(tg_chat_id, massage)
        timestamp = info_checkout['last_attempt_timestamp']
    else:
        timestamp = info_checkout['timestamp_to_request']
    return timestamp


def main():
    load_dotenv()

    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--chat_id',
                        type=int, help='The chat ID to use.',
                        default=os.environ.get('TG_CHAT_ID'))

    args = parser.parse_args()

    tg_chat_id = args.chat_id

    tg_token = os.environ['TELEGRAM_TOKEN']
    dm_token = os.environ['DEVMAN_TOKEN']
    max_retries = 5
    retry_count = 0
    timestamp = None

    while True:
        try:
            timestamp = get_homework_status(tg_chat_id,
                                            tg_token,
                                            dm_token,
                                            timestamp)
            retry_count = 0
        except ConnectionError as con_error:
            print(con_error)
            retry_count += 1
            if retry_count >= max_retries:
                time.sleep(30)
                retry_count = 0
        except requests.exceptions.ReadTimeout as rt_error:
            print(rt_error)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()
