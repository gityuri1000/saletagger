FROM python:3.9

WORKDIR /usr/src/myapp

COPY . .

RUN pip install --no-cache-dir -r utils/requirements.txt
# RUN python3 database_drivers/init_db.py

CMD [ "python3.9", "telegram_bot/main_bot.py" ]

