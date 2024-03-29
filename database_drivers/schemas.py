from pydantic import BaseModel

class AddedItemRow(BaseModel):
    user_name: str
    chat_id: int
    item_url: str
    shop: str

