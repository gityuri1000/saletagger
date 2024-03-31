import sys
sys.path.append("/home/yyy/Desktop/app_with_git/app")
# Для Docker
sys.path.append("/usr/src/myapp")

import os
import time
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Callable
from dotenv import load_dotenv
from database_drivers.cruds import update_parsed_item_table
from database_drivers.database_engine import SessionLocal
from parsers.parser_schemas import WebsiteItemData, ItemURL, WebsiteURL, WebsiteCategories, WebsiteCategoryURL, ShopName

load_dotenv(dotenv_path="/home/yyy/Desktop/app_with_git/app.env")
TOKEN = os.environ["TOKEN"]

def timer(func: Callable):
    def wrapper(self, website_url: WebsiteURL, *args, **kwargs):
        start = time.time()
        result = func(self, website_url)
        print(f"Время выполнения программы: {time.time() - start}")
        return result
    return wrapper

class BaseParser(ABC):
    def __init__(self, website_url: WebsiteURL, website_categories: WebsiteCategories, website_name: ShopName) -> None:
        self.website_categories = website_categories
        self.website_url = website_url
        self.website_name = website_name

    @abstractmethod
    def _make_result_by_category_url(self, website_category_url: WebsiteCategoryURL) -> List[WebsiteItemData]:
        pass

    @timer
    def get_data_from_web_site(self, website_url: WebsiteURL) -> Dict[ItemURL, WebsiteItemData]:
        print(f"Парсинг сайта: {website_url.url}", "\n")

        result: List[WebsiteItemData] = self._make_result_by_category_url(self.website_categories.categories[0])
        print(f"Завершение парсинга категории: {self.website_categories.categories[0]}")

        for category in self.website_categories.categories[1:]:
            if category.url:
                result.extend(self._make_result_by_category_url(website_category_url=category))
                print(f"Завершение парсинга категории: {category.url}")

        return {ItemURL(item_url=row.item_url): row for row in result}


    def update_data_in_parsed_items_table(self) -> None:
        parsed_data = self.get_data_from_web_site(self.website_url)
        print(len(parsed_data))
        asyncio.run(update_parsed_item_table(SessionLocal, parsed_data, parsed_shop=self.website_name))





        


    