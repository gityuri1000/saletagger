import sys
import time
sys.path.append("/home/yyy/Desktop/app_with_git/app")

from typing import Dict, List, Set
import requests
import re
from bs4 import BeautifulSoup
from parsers.base import BaseParser

class RedSeptemberParser(BaseParser):

    def __make_result_by_category_url(self, url: str) -> List[Dict]:
        page_number = 1
        result, items_name, items_url, items_price = list(), list(), list(), list()

        while True:
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
                "shop": "Red September",
                "current_price": items_price[i],
                "is_active": 1
                }
            )


        return result
    
    def get_data_from_web_site(self) -> List[Dict]:
        print("Парсинг сайта: https://redseptemberdesign.com", "\n")

        result: List[Dict] = self.__make_result_by_category_url("https://redseptemberdesign.com/collection/muzhskoe?page=")
        
        rest_categories = (
            "https://redseptemberdesign.com/collection/novinki?page=",
            "https://redseptemberdesign.com/collection/sale-2?page=",
            "https://redseptemberdesign.com/collection/verhnyaya-odezhda?page=",
            "https://redseptemberdesign.com/collection/kurtki-i-pidzhaki?page=",
            "https://redseptemberdesign.com/collection/svitera-i-kardigany?page=",
            "https://redseptemberdesign.com/collection/hudi-i-svitshoty?page=",
            "https://redseptemberdesign.com/collection/katalog-2-f845ef?page=",
            "https://redseptemberdesign.com/collection/futbolki-i-longslivy?page=",
            "https://redseptemberdesign.com/collection/katalog-2-55a2f0?page=",
            "https://redseptemberdesign.com/collection/bryuki-i-shorty?page=",
            "https://redseptemberdesign.com/collection/aksessuary?page=",
            
            "https://redseptemberdesign.com/collection/zhenskoe?page=",
            "https://redseptemberdesign.com/collection/novinki-2?page=",
            "https://redseptemberdesign.com/collection/sale-3?page=",
            "https://redseptemberdesign.com/collection/katalog-1-43b1f4?page=",
            "https://redseptemberdesign.com/collection/katalog-1-2c027b?page=",
            "https://redseptemberdesign.com/collection/katalog-1-c0c5aa?page=",
            "https://redseptemberdesign.com/collection/katalog-1-73ee53?page=",
            "https://redseptemberdesign.com/collection/futbolki-i-longslivy-2?page=",
            "https://redseptemberdesign.com/collection/katalog-1-cd9159?page=",
            "https://redseptemberdesign.com/collection/katalog-1-05b236?page=",
            "https://redseptemberdesign.com/collection/yubki-i-shorty?page=",
            "https://redseptemberdesign.com/collection/platya-i-rubashki?page="
        )

        for category in rest_categories:
            result.extend(self.__make_result_by_category_url(url=category))

        return list({row_dict["item_url"]: row_dict for row_dict in result}.values())
        
if __name__ == "__main__":
    red_september = RedSeptemberParser()
    red_september.update_data_in_parsed_items_table()