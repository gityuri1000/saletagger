import asyncio
import time
import sys
sys.path.append("/home/yyy/Desktop/app_with_git/app")
from abc import ABC, abstractmethod
from typing import Dict, List, Union
from sqlalchemy.ext.asyncio import AsyncEngine
from database_drivers.cruds import get_query_from_parsed_item_table
from database_drivers.cruds import set_data_to_parsed_item_table
from database_drivers.cruds import update_parsed_item_table
from database_drivers.cruds import set_data_to_added_users_item_table
from database_drivers.database_engine import SessionLocal

class BaseParser(ABC):
    # @abstractmethod
    def __make_result_by_category_url(self, url: str) -> List[Dict]:
        pass

    @abstractmethod
    def get_data_from_web_site(self) -> Dict[str, Dict]:
        pass

    def update_data_in_parsed_items_table(self) -> None:
        parsed_data = self.get_data_from_web_site()
        asyncio.run(update_parsed_item_table(SessionLocal, parsed_data))

    def add_data_to_added_users_item_table(self, data_from_bot) -> None:
        asyncio.run(set_data_to_added_users_item_table(data_from_bot))

if __name__ == "__main__":
    parser = BaseParser()   
    parser.update_data_in_parsed_items_table()


        


    