import sys
sys.path.append("/home/yyy/Desktop/app_with_git/app")

import os
import time
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Callable
from dotenv import load_dotenv
from database_drivers.cruds import update_parsed_item_table
from database_drivers.database_engine import SessionLocal
from parsers.parser_schemas import WebsiteItemData, ItemURL

load_dotenv(dotenv_path="/home/yyy/Desktop/app_with_git/app.env")
TOKEN = os.environ["TOKEN"]

class BaseParser(ABC):
    @abstractmethod
    def get_data_from_web_site(self) -> Dict[ItemURL, WebsiteItemData]:
        pass

    def update_data_in_parsed_items_table(self) -> None:
        parsed_data = self.get_data_from_web_site()
        asyncio.run(update_parsed_item_table(SessionLocal, parsed_data))

def timer(func: Callable):
    def wrapper(self, *args, **kwargs):
        start = time.time()
        result = func(self)
        print(f"Время выполнения программы: {time.time() - start}")
        return result
    return wrapper



        


    