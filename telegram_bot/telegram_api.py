import requests
from parsers.parser_schemas import ItemURL

def send_changed_price_message(token: str, chat_id: int, item_url: ItemURL):
    requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text=Изменилась цена на товар: {item_url}&disable_web_page_preview=true")

def send_del_item_message(token: str, chat_id: int, item_url: ItemURL):
    requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text=Товар убран из продажи: {item_url}&disable_web_page_preview=true") 

def send_again_in_stock_message(token: str, chat_id: int, item_url: ItemURL):
    requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text=Товар снова в продаже: {item_url}&disable_web_page_preview=true")