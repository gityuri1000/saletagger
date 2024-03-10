import sys
from typing import Dict, List
sys.path.append("/home/yyy/Desktop/practis+git/app")
# sys.path.append("/home/yyy/Desktop/practis+git/app/database_drivers")

import requests
import re
from bs4 import BeautifulSoup
from parsers.base import BaseParser
# from database_drivers.database_engine import SessionLocal

class RogovParser(BaseParser):

    def __make_result_by_category_url(self, url: str) -> List[Dict]:

        page_number = 2
        result, items_name, items_url, items_price = list(), list(), list(), list()
        # soup_by_url = BeautifulSoup(requests.get(url + str(page_number)).text, "html.parser")
        
        while True:
            req = requests.get(url + str(page_number)).text
            soup_by_url = BeautifulSoup(req, "html.parser")
            
            if page_number == 3:
                break

            if soup_by_url.find("main").find("div", class_="redisign").find("p") != None:
                category_name = url.rstrip("page=")[:-1]
                print(f"Завершение парсинга категории: {category_name}")
                break

            result_for_names_and_urls: List = soup_by_url.find_all("div", class_="item-info__name")
            
            for item_html_data in result_for_names_and_urls:
                # if page_number == 2:
                #     print(item_html_data)
                soup_by_page = BeautifulSoup(str(item_html_data), "html.parser")
                items_url.append(soup_by_page.find("a")["href"])
                items_name.append(soup_by_page.find("a").text.strip())

            result_for_prices: List = soup_by_url.find_all("div", class_="item-info__price")

            for i in range(len(result_for_prices)):

                soup_by_page = BeautifulSoup(str(result_for_prices[i]), "html.parser")
                price_to_add = re.sub("[^0-9]", "", soup_by_page.find("span").text)
                price_to_add = 0 if price_to_add == "" else price_to_add
                items_price.append(int(price_to_add))

                result.append(
                    {
                    "item_name": items_name[i], 
                    "item_url": items_url[i],
                    "shop": "Rogov",
                    "current_price": items_price[i],
                    "is_active": True
                    }
                )

            page_number += 1
        
        return result
        
    def get_data_from_web_site(self) -> List[Dict]:
        print("Парсинг сайта: https://rogovshop.ru", "\n")

        result: List[Dict] = self.__make_result_by_category_url("https://rogovshop.ru/dly-nego?page=")
        # result.extend(self.__make_result_by_category_url("https://rogovshop.ru/dly-nee?page="))
        # result.extend(self.__make_result_by_category_url("https://rogovshop.ru/baza?page="))
        # result.extend(self.__make_result_by_category_url("https://rogovshop.ru/sale?page="))
        # result.extend(self.__make_result_by_category_url("https://rogovshop.ru/nizhnee-belie?page="))
        # result.extend(self.__make_result_by_category_url("https://rogovshop.ru/trikotazh?page="))
        # result.extend(self.__make_result_by_category_url("https://rogovshop.ru/verkhniaia-odezhda?page="))
        # result.extend(self.__make_result_by_category_url("https://rogovshop.ru/gift-certificate?page="))
        return result

if __name__ == "__main__":
    rogov = RogovParser()
    rogov.update_data_in_parsed_items_table()
