FROM python:3.9

WORKDIR /usr/src/telegram_bot

COPY ./requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./main_bot.py ./
COPY ./main_database.py ./

COPY ./database_drivers/. ./database_drivers/

CMD [ "python3.9", "main_bot.py" ]

