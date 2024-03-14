import sys
from typing import Dict, List, Set
sys.path.append("/home/yyy/Desktop/app_with_git/app")

import requests
import re
from bs4 import BeautifulSoup
from parsers.base import BaseParser

class RogovParser(BaseParser):

    def __make_result_by_category_url(self, url: str) -> List[Dict]:
        page_number = 1
        result, items_name, items_url, items_price = list(), list(), list(), list()
        
        while True:
            req = requests.get(url + str(page_number)).text
            soup_by_url = BeautifulSoup(req, "html.parser")

            if soup_by_url.find("main").find("div", class_="redisign").find("p") != None:
                category_name = url.rstrip("page=")[:-1]
                print(f"Завершение парсинга категории: {category_name}")
                break

            result_for_names_and_urls: List = soup_by_url.find_all("div", class_="item-info__name")
            
            for item_html_data in result_for_names_and_urls:
                soup_by_page = BeautifulSoup(str(item_html_data), "html.parser")
                items_url.append(soup_by_page.find("a")["href"])
                items_name.append(soup_by_page.find("a").text.strip())

            result_for_prices: List = soup_by_url.find_all("div", class_="item-info__price")

            for item_html_data in (result_for_prices):
                soup_by_page = BeautifulSoup(str(item_html_data), "html.parser")
                price_to_add = re.sub("[^0-9]", "", soup_by_page.find("span").text)
                price_to_add = 0 if price_to_add == "" else price_to_add
                items_price.append(int(price_to_add))

            page_number += 1

        for i in range(len(items_url)):
            result.append(
                {
                "item_name": items_name[i], 
                "item_url": items_url[i],
                "shop": "Rogov",
                "current_price": items_price[i],
                "is_active": 1
                }
            )
       
        return result
    
    
        
    def get_data_from_web_site(self) -> List[Dict]:
        print("Парсинг сайта: https://rogovshop.ru", "\n")

        result: List[Dict] = self.__make_result_by_category_url("https://rogovshop.ru/dly-nego?page=")

        rest_categories = (
            # "https://rogovshop.ru/dly-nee?page=",
            # "https://rogovshop.ru/baza?page=",
            # "https://rogovshop.ru/sale?page=",
            # "https://rogovshop.ru/nizhnee-belie?page=",
            # "https://rogovshop.ru/trikotazh?page=",
            # "https://rogovshop.ru/verkhniaia-odezhda?page=",
            # "https://rogovshop.ru/gift-certificate?page=",

        )

        for category in rest_categories:
            result.extend(self.__make_result_by_category_url(url=category))
        
        return list({row_dict["item_url"]: row_dict for row_dict in result}.values())


if __name__ == "__main__":
    rogov = RogovParser()
    rogov.update_data_in_parsed_items_table()
