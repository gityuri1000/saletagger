import sys
sys.path.append("/home/yyy/Desktop/app_with_git/app")

import time
import asyncio
from abc import ABC, abstractmethod
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncEngine
from database_drivers.cruds import get_query_from_parsed_item_table
from database_drivers.cruds import set_data_to_parsed_item_table
from database_drivers.cruds import update_parsed_item_table
from database_drivers.cruds import set_data_to_added_users_item_table
from database_drivers.database_engine import SessionLocal
from schemas import WebsiteItemData

class BaseParser(ABC):
    
    @abstractmethod
    def get_data_from_web_site(self) -> Dict[str, WebsiteItemData]:
        pass

    def update_data_in_parsed_items_table(self) -> None:
        parsed_data = self.get_data_from_web_site()
        asyncio.run(update_parsed_item_table(SessionLocal, parsed_data))




        


    