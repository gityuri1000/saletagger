FROM python:3.9

WORKDIR /usr/src/telegram_bot

COPY ./ ./

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python3.9", "main_bot.py" ]

