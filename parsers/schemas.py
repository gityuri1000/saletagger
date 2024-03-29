from typing import Union
from pydantic import BaseModel

class WebsiteItemData(BaseModel):
    item_name: str
    item_url: str
    shop: str
    current_price: Union[int, float]
    is_active: int