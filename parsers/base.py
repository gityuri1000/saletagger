import asyncio
import sys
sys.path.append("/home/yyy/Desktop/practis+git/app")
# sys.path.append("/home/yyy/Desktop/practis+git/app/database_drivers")
from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncEngine
from database_drivers.cruds import get_query_from_parsed_item_table
from database_drivers.cruds import set_data_to_parsed_item_table
from database_drivers.cruds import update_parsed_item_table
from database_drivers.cruds import set_data_to_added_users_item_table
#
from database_drivers.database_engine import SessionLocal, async_engine

class BaseParser:
    session = SessionLocal

    def get_data_from_web_site(self) -> List[Dict]:
        test_initial_add_list = [
            {'item_name': 'test_name_1', 'item_url': 'www.test_url_1.com', 'shop': 'shop_1', 'current_price': 2132, 'is_active': True},
            {'item_name': 'test_name_2', 'item_url': 'www.test_url_2.com', 'shop': 'shop_2', 'current_price': 2199, 'is_active': True},
            {'item_name': 'test_name_4', 'item_url': 'www.test_url_4.com', 'shop': 'shop_2', 'current_price': 2142, 'is_active': True},
            {'item_name': 'test_name_5', 'item_url': 'www.test_url_5.com', 'shop': 'shop_4', 'current_price': 2442, 'is_active': True},
            {'item_name': 'test_name_6', 'item_url': 'www.test_url_6.com', 'shop': 'shop_2', 'current_price': 2842, 'is_active': True},
            {'item_name': 'test_name_3', 'item_url': 'www.test_url_3.com', 'shop': 'shop_3', 'current_price': 2100, 'is_active': True},
            {'item_name': 'test_name_7', 'item_url': 'www.test_url_7.com', 'shop': 'shop_3', 'current_price': 2100, 'is_active': True},
            {'item_name': 'test_name_8', 'item_url': 'www.test_url_8.com', 'shop': 'shop_4', 'current_price': 2442, 'is_active': True},
            # {'item_name': 'test_name_9', 'item_url': 'www.test_url_9.com', 'shop': 'shop_4', 'current_price': 2842, 'is_active': True}

        ]

        # print('Write your parser code in this method with dict return')
        return test_initial_add_list

    def update_data_in_parsed_items_table(self) -> None:
        parsed_data = self.get_data_from_web_site()
        asyncio.run(update_parsed_item_table(SessionLocal, parsed_data))

    def add_data_to_added_users_item_table(self, data_from_bot) -> None:
        asyncio.run(set_data_to_added_users_item_table(data_from_bot))

if __name__ == "__main__":
    parser = BaseParser()   
    parser.update_data_in_parsed_items_table()


        


    