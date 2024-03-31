from typing import Union, Sequence, Annotated
from pydantic import BaseModel

class WebsiteURL(BaseModel):
    url: str

class WebsiteCategoryURL(BaseModel):
    url: str

class WebsiteCategories(BaseModel):
    categories: Sequence[WebsiteCategoryURL]

class ItemURL(BaseModel):
    item_url: str

    def __hash__(self) -> int:
        return hash(self.item_url)

class WebsiteItemData(BaseModel):
    item_name: str
    item_url: str
    shop: str
    current_price: Union[int, float]
    is_active: int

ShopName = str


