from typing import Union, Sequence, Annotated
from pydantic import BaseModel
from enum import Enum

class WebsiteCategoryURL(BaseModel):
    """
    Pydantic. Класс для валидации ссылок на категории сайта.

    Структура:

    url: str;

    """

    url: str

class WebsiteCategories(BaseModel):
    """
    Pydantic. Класс для валидации списка url-категорий сайта.

    Структура:

    categories: Sequence[WebsiteCategoryURL];

    """


    categories: Sequence[WebsiteCategoryURL]

class ItemURL(BaseModel):
    """
    Pydantic. Валидация ссылки на товар.

    Структура:

    item_url: str;

    """

    item_url: str

    def __hash__(self) -> int:
        return hash(self.item_url)

class WebsiteItemData(BaseModel):
    """
    Pydantic. Объекты данного класса - информация 
    о вещи, находящейся на сайте. Далее помещается
    в таблицу parsed_item_table.

    Структура:

    item_name: str;
    item_url: str;
    shop: str;
    current_price: Union[int, float];
    is_active: int;

    """

    item_name: str
    item_url: str
    shop: str
    current_price: Union[int, float]
    is_active: int

class WebsiteURL(Enum):
    """
    Enum. Содержит ссылки на сайты,
    с которых собирается информация о товарах.

    Значения:

    Rogov = "rogovshop.ru";
    RedSeptember = "redseptemberdesign.com";
    Fable = "https://fablestore.ru";

    """

    Rogov = "rogovshop.ru"
    RedSeptember = "redseptemberdesign.com"
    Fable = "https://fablestore.ru"

class ShopName(Enum):
    """
    Enum. Содержит названия магазинов,
    с которых собирается инфомация о товарах.

    Значения:

    Rogov = "Rogov";
    RedSeptember = "Red September";
    Fable = "Fable";

    """

    Rogov = "Rogov"
    RedSeptember = "Red September"
    Fable = "Fable"


