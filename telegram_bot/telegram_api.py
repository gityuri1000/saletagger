import requests
from typing import List, Union
from parsers.parser_schemas import ItemURL
from database_drivers.schemas import AddedItemRow

def send_changed_price_message(token: str, chat_id: Union[int, None], needs_message_urls: List[AddedItemRow]):
    if chat_id == None:
        return

    message_text = ""
    for row in needs_message_urls:
        message_text += f"Изменилась цена на товар: {row.item_url}\n"

    requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message_text}&disable_web_page_preview=true")

def send_del_item_message(token: str, chat_id: Union[int, None], needs_message_urls: List[AddedItemRow]):
    if chat_id == None:
        return

    message_text = ""
    for row in needs_message_urls:
        message_text += f"Товар убран из продажи: {row.item_url}\n"

    print(message_text)
    requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message_text}&disable_web_page_preview=true") 

def send_again_in_stock_message(token: str, chat_id: Union[int, None], needs_message_urls: List[AddedItemRow]):
    if chat_id == None:
        return

    message_text = ""
    for row in needs_message_urls:
        message_text += f"Товар снова в продаже: {row.item_url}\n"

    print(message_text)
    requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message_text}&disable_web_page_preview=true")