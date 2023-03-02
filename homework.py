import logging
import os
import sys
import time
from http import HTTPStatus
from json.decoder import JSONDecodeError

import requests
import telegram
from dotenv import load_dotenv


load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)) is False:
        tokens = []

        if PRACTICUM_TOKEN is None:
            tokens.append('PRACTICUM_TOKEN')
        if TELEGRAM_TOKEN is None:
            tokens.append('TELEGRAM_TOKEN')
        if TELEGRAM_CHAT_ID is None:
            tokens.append('TELEGRAM_CHAT_ID')

        message = f'Отсутствуют обязательные переменные окружения: {tokens}.'
        logging.critical(message)
        raise ValueError(message)


def send_message(bot, message):
    """Отправляет сообщение в Telegram-чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug(f'Бот отправил сообщение: {message}.')
    except telegram.error.TelegramError as error:
        logging.error(f'Сбой при отправке сообщения в Telegram: {error}.')


def get_api_answer(timestamp):
    """Делает запрос к эндпоинту API-сервиса."""
    payload = {'from_date': timestamp}

    try:
        response = requests.get(url=ENDPOINT, headers=HEADERS, params=payload)
    except requests.RequestException as error:
        logging.error(f'Сбой при запросе к эндпоинту {ENDPOINT}: {error}.')

    if response.status_code != HTTPStatus.OK:
        message = f'Недоступен эндпоинт {ENDPOINT}.'
        logging.error(message)
        raise ConnectionError(message)

    try:
        return response.json()
    except JSONDecodeError as error:
        message = f'Ответ сервера не преобразовывался в JSON: {error}'
        logging.error(message)
        raise JSONDecodeError(message)


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    api_answers_types = {
        'homeworks': list,
        'current_date': int
    }

    if not isinstance(response, dict):
        raise TypeError('Ответ API не является словарём.')

    for key, value in api_answers_types.items():
        if key not in response:
            logging.error(f'Отсутствует ключ {key}.')
            raise KeyError(f'Отсутствует ключ {key}.')
        if not isinstance(response[key], value):
            raise TypeError('Ответ API не соответствует документации.')


def parse_status(homework):
    """Извлекает из информации о домашней работе статус этой работы."""
    homework_name = homework.get('homework_name')

    if homework_name is None:
        message = 'Отсутствует ключ homework_name.'
        logging.error(message)
        raise KeyError(message)

    status = homework.get('status')
    verdict = HOMEWORK_VERDICTS.get(status)

    if verdict is None:
        message = f'Неожиданный статус домашней работы: {status}.'
        logging.error(message)
        raise KeyError(message)

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time()) - RETRY_PERIOD
    old_message = ''

    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            homeworks = response.get('homeworks')

            if homeworks:
                homework = homeworks[0]
                message = parse_status(homework)
                send_message(bot, message)
            else:
                logging.debug('В ответе отсутствуют новые статусы.')

            timestamp = response.get('current_date')
            old_message = ''
        except Exception as error:
            message = f'Сбой в работе программы: {error}'

            if message != old_message:
                old_message = message
                send_message(bot, message)

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        handlers=[logging.StreamHandler(sys.stdout)],
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )

    main()
