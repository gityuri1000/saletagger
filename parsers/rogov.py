import sys
sys.path.append("/home/yyy/Desktop/app_with_git/app")
# Для Docker
sys.path.append("/usr/src/myapp")

import re
import requests
from typing import List
from bs4 import BeautifulSoup
from parsers.base import BaseParser, timer
from parsers.parser_schemas import WebsiteItemData, WebsiteCategories, WebsiteCategoryURL, WebsiteURL

class RogovParser(BaseParser):

    def _make_result_by_category_url(self, website_category_url: WebsiteCategoryURL) -> List[WebsiteItemData]:
        page_number = 1
        result, items_name, items_url, items_price = list(), list(), list(), list()
        
        while True:
            req = requests.get(website_category_url.url + str(page_number)).text
            soup_by_url = BeautifulSoup(req, "html.parser")

            if soup_by_url.find("main").find("div", class_="redisign").find("p") != None:
                category_name = website_category_url.url.rstrip("page=")[:-1]
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
                WebsiteItemData(
                    item_name=items_name[i],
                    item_url=items_url[i],
                    shop=self.website_name,
                    current_price=items_price[i],
                    is_active=1
                )
            )

        return result

rogov_categories = WebsiteCategories(categories=
    (
        WebsiteCategoryURL(url="https://rogovshop.ru/dly-nego?page="),
        # WebsiteCategoryURL(url="https://rogovshop.ru/dly-nee?page="),
        # WebsiteCategoryURL(url="https://rogovshop.ru/baza?page="),
        # WebsiteCategoryURL(url="https://rogovshop.ru/sale?page="),
        # WebsiteCategoryURL(url="https://rogovshop.ru/nizhnee-belie?page="),
        # WebsiteCategoryURL(url="https://rogovshop.ru/trikotazh?page="),
        # WebsiteCategoryURL(url="https://rogovshop.ru/verkhniaia-odezhda?page="),
        # WebsiteCategoryURL(url="https://rogovshop.ru/gift-certificate?page=")
    )
)

if __name__ == "__main__":
    rogov = RogovParser(website_url=WebsiteURL(url="rogovshop.ru"), website_categories=rogov_categories, website_name="Rogov")
    rogov.update_data_in_parsed_items_table()

