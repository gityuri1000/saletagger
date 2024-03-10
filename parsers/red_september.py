import sys
import time
sys.path.append("/home/yyy/Desktop/practis+git/app")

from typing import Dict, List
import requests
import re
from bs4 import BeautifulSoup
from parsers.base import BaseParser

class RedSeptemberParser(BaseParser):

    def __make_result_by_category_url(self, url: str) -> List[Dict]:
        
        page_number = 1
        result, items_name, items_url, items_price = [], [], [], []

        while True:
            print(f"url: {url + str(page_number)}")
            soup_by_url = BeautifulSoup(requests.get(url + str(page_number)).text, "html.parser")

            if soup_by_url.find("main").find("div", class_="empty-catalog-message") != None:
                category_name = url.rstrip("page=")[:-1]
                print(f"Завершение парсинга категории: {category_name}")
                break

            result_for_names_and_urls: List = soup_by_url.find_all("div", class_="product-preview__title")
            
            for item_html_data in result_for_names_and_urls:
                soup_by_page = BeautifulSoup(str(item_html_data), "html.parser")
                items_name.append(soup_by_page.find("a").text.strip())
                items_url.append("https://redseptemberdesign.com" + soup_by_page.find("a")["href"])

            result_for_prices: List = soup_by_url.find_all("span", class_="product-preview__price-cur")

            for i in range(len(result_for_prices)):
                soup_by_page = BeautifulSoup(str(result_for_prices[i]), "html.parser")
                price_to_add = re.sub("[^0-9]", "", soup_by_page.find("span").text)
                price_to_add = 0 if price_to_add == "" else price_to_add
                items_price.append(int(price_to_add))

                result.append(
                    {
                    "item_name": items_name[i], 
                    "item_url": items_url[i],
                    "shop": "Red September",
                    "current_price": items_price[i],
                    "is_active": True
                    }
                )

            page_number += 1

        return result

    def get_data_from_web_site(self) -> List[Dict]:
        print("Парсинг сайта: https://redseptemberdesign.com", "\n")

        result = self.__make_result_by_category_url("https://redseptemberdesign.com/collection/muzhskoe?page=")
        return result


if __name__ == "__main__":
    red_september = RedSeptemberParser()
    red_september.update_data_in_parsed_items_table()