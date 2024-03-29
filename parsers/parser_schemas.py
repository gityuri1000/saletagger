from typing import Union
from pydantic import BaseModel

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
