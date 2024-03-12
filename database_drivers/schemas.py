from typing import Union, List
from pydantic import BaseModel

class ItemInputRow(BaseModel):
    item_name: str
    item_url: str
    shop: str
    current_price: Union[int, float]
    is_active: bool

class ItemInputList(BaseModel):
    data_to_input: List[ItemInputRow]

class AddedItemDict(BaseModel):
    user_name: str
    chat_id: int
    item_url: str
    shop: str

