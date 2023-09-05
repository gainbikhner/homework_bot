# Телеграм-бот для проверки статуса домашней работы на код ревью в Яндекс.Практикум

## Автор

https://github.com/gainbikhner

## Описание

Бот работающий с API Яндекс.Практикум. Каждые 10 минут бот проверяет API Яндекс.Практикум и отправляет сообщение в Телеграм.  

У API Практикум.Домашка есть лишь один эндпоинт:  

https://practicum.yandex.ru/api/user_api/homework_statuses/

Получить токен можно по [адресу](https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a)

## Принцип работы API

Когда ревьюер проверяет вашу домашнюю работу, бот присваивает ей один из статусов:

- работа принята на проверку
- работа возвращена для исправления ошибок
- работа принята

## Установка

1. Скопируйте проект.

```
git clone git@github.com:gainbikhner/homework_bot.git
```

2. Перейдите в папку с ботом.

```
cd homework_bot
```

3. Установите и активируйте виртуальное окружение.

```
python -m venv venv
source venv/Scripts/activate
```

4. Установите зависимости.

```
pip install -r requirements.txt
```

5. Создайте .env с PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID.

6. Запустите бота.

```
python homework.py
```
