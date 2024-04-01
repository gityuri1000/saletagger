import sys
sys.path.append("/home/yyy/Desktop/app_with_git/app")
# Для Docker
sys.path.append("/usr/src/myapp")


import re
import copy
import requests
from typing import List
from bs4 import BeautifulSoup
from parsers.base import BaseParser
from parsers.parser_schemas import WebsiteURL, WebsiteCategoryURL, WebsiteCategories, WebsiteItemData, ShopName



class FableParser(BaseParser):


    def _make_result_by_category_url(self, website_category_url: WebsiteCategoryURL) -> List[WebsiteItemData]:
        page_number = 1
        result, items_name, items_url, items_price = list(), list(), list(), list()

        while True:
            req = requests.get(website_category_url.url + str(page_number)).text
            soup_by_url = BeautifulSoup(req, "html.parser")

            result_for_names_and_prices = soup_by_url.find_all("div", class_="product-card__content")

            if page_number == 1:
                stop_page = result_for_names_and_prices

            if page_number != 1 and result_for_names_and_prices == stop_page:
                break

            if page_number == 100:
                print("break 100!")
                break

            for item_html_data in result_for_names_and_prices:
                soup_by_page = BeautifulSoup(str(item_html_data), "html.parser")
                items_name.append(soup_by_page.find("div", class_="product-card__title body-text").text.strip())
                price_to_add = re.sub("[^0-9]", "", soup_by_page.find("span").text)
                price_to_add = 0 if price_to_add == "" else price_to_add
                items_price.append(int(price_to_add))

            result_for_urls = soup_by_url.find_all("a", class_="catalog-content__item product-card product-card-listing")

            for item_html_data in result_for_urls:
                items_url.append("https://fablestore.ru" + item_html_data["href"])

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

fable_categories = WebsiteCategories(categories=
    (
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/sale/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/man/pukhoviki_3/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/man/outerwear/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/man/zhilety_3/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/man/sweatshirts/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/man/knitted/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/man/blazers/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/man/shirts/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/man/pants/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/man/longsleeves/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/man/t-shirts/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/man/shorts/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/man/new/?PAGEN_2="),

        WebsiteCategoryURL(url="https://fablestore.ru/catalog/woman/sale_w/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/woman/pukhoviki_2/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/woman/zhilety_4/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/woman/sweatshirts_w/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/woman/knitted_w/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/woman/blazers_w/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/woman/dresses_w/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/woman/shirts_w/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/woman/longsleeves_w/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/woman/t-shirts_w/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/woman/tops_w/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/woman/skirts_w/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/woman/pants_w/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/woman/shorts_w/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/woman/new_w/?PAGEN_2="),

        WebsiteCategoryURL(url="https://fablestore.ru/catalog/collections/lovehunter/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/univermag/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/dinamo/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/collections/fable-of-essense/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/collections/fable-of-office/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/collections/fable-of-basic/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/collections/fable-of-destroy/?PAGEN_2="), 
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/collections/fable-of-klassik-2-0/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/collections/fable-of-track/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/collections/fable-of-jpeg/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/collections/fable-of-dirty/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/collections/fable-of-klassik/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/collections/fable-of-colors/?PAGEN_2="),

        WebsiteCategoryURL(url="https://fablestore.ru/catalog/constructors/?PAGEN_2="),

        WebsiteCategoryURL(url="https://fablestore.ru/catalog/accessories/panamy/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/accessories/socks/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/accessories/ties/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/accessories/pins/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/accessories/sharfy/?PAGEN_2="),
        WebsiteCategoryURL(url="https://fablestore.ru/catalog/accessories/shapki/?PAGEN_2="),

        WebsiteCategoryURL(url="https://fablestore.ru/catalog/sale/?PAGEN_2=")
    )

)

if __name__ == "__main__":
    fable = FableParser(website_url=WebsiteURL.Fable, website_categories=fable_categories, website_name=ShopName.Fable)
    fable.update_data_in_parsed_items_table()
