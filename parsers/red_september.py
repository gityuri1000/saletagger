import sys
sys.path.append("/home/yyy/Desktop/app_with_git/app")
# Для Docker
sys.path.append("/usr/src/myapp")

import re
import requests
from typing import List
from bs4 import BeautifulSoup
from parsers.base import BaseParser
from parsers.parser_schemas import WebsiteItemData, WebsiteURL, WebsiteCategories, WebsiteCategoryURL

class RedSeptemberParser(BaseParser):
    def _make_result_by_category_url(self, website_category_url: WebsiteCategoryURL) -> List[WebsiteItemData]:
        page_number = 1
        result, items_name, items_url, items_price = list(), list(), list(), list()

        while True:
            soup_by_url = BeautifulSoup(requests.get(website_category_url.url + str(page_number)).text, "html.parser")

            if soup_by_url.find("main").find("div", class_="empty-catalog-message") != None:
                category_name = website_category_url.url.rstrip("page=")[:-1]
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
                WebsiteItemData(
                    item_name=items_name[i],
                    item_url=items_url[i],
                    shop=self.website_name,
                    current_price=items_price[i],
                    is_active=1
                )
            )

        return result
    

red_september_categories = WebsiteCategories(
    categories = (
            WebsiteCategoryURL(url="https://redseptemberdesign.com/collection/novinki?page="),
            # WebsiteCategoryURL(url="https://redseptemberdesign.com/collection/sale-2?page="),
            # WebsiteCategoryURL(url="https://redseptemberdesign.com/collection/verhnyaya-odezhda?page="),
            # WebsiteCategoryURL(url="https://redseptemberdesign.com/collection/kurtki-i-pidzhaki?page="),
            # WebsiteCategoryURL(url="https://redseptemberdesign.com/collection/svitera-i-kardigany?page="),
            # WebsiteCategoryURL(url="https://redseptemberdesign.com/collection/hudi-i-svitshoty?page="),
            # WebsiteCategoryURL(url="https://redseptemberdesign.com/collection/katalog-2-f845ef?page="),
            # WebsiteCategoryURL(url="https://redseptemberdesign.com/collection/futbolki-i-longslivy?page="),
            # WebsiteCategoryURL(url="https://redseptemberdesign.com/collection/katalog-2-55a2f0?page="),
            # WebsiteCategoryURL(url="https://redseptemberdesign.com/collection/bryuki-i-shorty?page="),
            # WebsiteCategoryURL(url="https://redseptemberdesign.com/collection/aksessuary?page="),
            
            # WebsiteCategoryURL(url="https://redseptemberdesign.com/collection/zhenskoe?page="),
            # WebsiteCategoryURL(url="https://redseptemberdesign.com/collection/novinki-2?page="),
            # WebsiteCategoryURL(url="https://redseptemberdesign.com/collection/sale-3?page="),
            # WebsiteCategoryURL(url="https://redseptemberdesign.com/collection/katalog-1-43b1f4?page="),
            # WebsiteCategoryURL(url="https://redseptemberdesign.com/collection/katalog-1-2c027b?page="),
            # WebsiteCategoryURL(url="https://redseptemberdesign.com/collection/katalog-1-c0c5aa?page="),
            # WebsiteCategoryURL(url="https://redseptemberdesign.com/collection/katalog-1-73ee53?page="),
            # WebsiteCategoryURL(url="https://redseptemberdesign.com/collection/futbolki-i-longslivy-2?page="),
            # WebsiteCategoryURL(url="https://redseptemberdesign.com/collection/katalog-1-cd9159?page="),
            # WebsiteCategoryURL(url="https://redseptemberdesign.com/collection/katalog-1-05b236?page="),
            # WebsiteCategoryURL(url="https://redseptemberdesign.com/collection/yubki-i-shorty?page="),
            # WebsiteCategoryURL(url="https://redseptemberdesign.com/collection/platya-i-rubashki?page=")
    )
)

if __name__ == "__main__":
    red_september = RedSeptemberParser(website_url=WebsiteURL(url="redseptemberdesign.com"), website_categories=red_september_categories, website_name="Red September")
    red_september.update_data_in_parsed_items_table()