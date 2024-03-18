from typing import Union, List, Dict
from pydantic import BaseModel

class ItemInputDictValue(BaseModel):
    item_name: str
    item_url: str
    shop: str
    current_price: Union[int, float]
    is_active: bool

class ItemInputDict(BaseModel):
    data_to_input: Dict[str, ItemInputDictValue]

class AddedItemDict(BaseModel):
    user_name: str
    chat_id: int
    item_url: str
    shop: str

