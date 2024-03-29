import sys
sys.path.append("/home/yyy/Desktop/app_with_git/app")

import os
import requests
from dotenv import load_dotenv
from typing import List, Dict
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, AsyncSession, async_sessionmaker
from database_drivers.models import Item, AddedItem
from database_drivers.schemas import AddedItemRow
from parsers.parser_schemas import WebsiteItemData, ItemURL

load_dotenv(dotenv_path="/home/yyy/Desktop/app_with_git/app/.env")
TOKEN = os.environ["TOKEN"]

async def set_data_to_parsed_item_table(session: AsyncSession, data: Dict[ItemURL, WebsiteItemData]) -> None:

    for row in data.values():
        item = Item(
            item_name = row.item_name,
            item_url = row.item_url,
            shop = row.shop,
            current_price = row.current_price,
            is_active = row.is_active
        )

        session.add(item)

async def change_current_price_in_parsed_item_table(session: AsyncSession, data: Dict[ItemURL, WebsiteItemData]) -> None:
    need_message_urls: List[ItemURL] = []

    for row in data.values():
        stmt = (
            update(Item)
            .where(Item.item_url.in_([row.item_url]))
            .values(current_price=row.current_price)
        )

        need_message_urls.append(ItemURL(row.item_url))
        await session.execute(stmt)
    
    list_of_need_message_rows: List[AddedItemRow] = await get_query_from_added_users_item_table_with_list_of_urls(session, need_message_urls)
    

    for row in list_of_need_message_rows:
        requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={row.chat_id}&text=Изменилась цена на товар: {row.item_url}&disable_web_page_preview=true")
        
async def get_query_from_parsed_item_table(session: AsyncSession) -> Dict[ItemURL, WebsiteItemData]:
    result = {}

    rows = select(Item)
    scalars = await session.scalars(rows)
    for row in scalars:
        row.__dict__.pop("_sa_instance_state")
        # row.__dict__.pop("id")
        result[ItemURL(row.__dict__["item_url"])] = WebsiteItemData(**row.__dict__)

    return result

async def deactivate_rows_in_parsed_item_table(
        session: AsyncSession,
        current_table_data: Dict[ItemURL, WebsiteItemData],
        new_table_data: Dict[ItemURL, WebsiteItemData],
        list_of_active_rows: List[ItemURL]
        ) -> None:
    need_message_urls: List[ItemURL] = []

    for row in current_table_data:
        if row not in new_table_data and row in list_of_active_rows:
            stmt = (update(Item)
                .where(Item.item_url == row.item_url)
                .values(is_active = 0)
            )

            need_message_urls.append(row)
            await session.execute(stmt)

    list_of_need_message_rows: List[AddedItemRow] = await get_query_from_added_users_item_table_with_list_of_urls(session, need_message_urls)

    for row in list_of_need_message_rows:
        requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={row.chat_id}&text=Товар убран из продажи: {row.item_url}&disable_web_page_preview=true")     

async def activate_rows_in_parsed_item_table(
        session: AsyncSession,
        current_table_data: Dict[ItemURL, WebsiteItemData], 
        new_table_data: Dict[ItemURL, WebsiteItemData], 
        current_not_active_urls_list: List[ItemURL]
    ) -> None:
    need_message_urls: List[ItemURL] = []

    for row in new_table_data.values():
        if row not in current_table_data.values() and row.item_url in current_not_active_urls_list:
            stmt = (update(Item)
                .where(Item.item_url == row.item_url)
                .values(is_active = 1)
            )

            need_message_urls.append(row.item_url)
            await session.execute(stmt)

    list_of_need_message_rows: List[AddedItemRow] = await get_query_from_added_users_item_table_with_list_of_urls(session, need_message_urls)

    for row in list_of_need_message_rows:
        requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={row.chat_id}&text=Товар снова в продаже: {row.item_url}&disable_web_page_preview=true")    

async def update_parsed_item_table(session: async_sessionmaker, new_table_data: Dict[ItemURL, WebsiteItemData]) -> None:
    async with session() as current_session:
        #Получаем данные из текущей таблицы, удаляя при этом столбец "id"
        current_table: Dict[ItemURL, WebsiteItemData] = await get_query_from_parsed_item_table(current_session)

        #Список из URL из текущей таблицы, у которых is_active = 0
        list_off_current_table_not_active_urls: List[ItemURL] = [key for key in current_table if current_table[key].is_active == 0]
        #Список из URL из текущей таблицы, у которых is_active = 1
        list_off_current_table_active_urls: List[ItemURL] = [key for key in current_table if current_table[key].is_active == 1]
        
        #Если данные из текущей таблицы и новые данные равны, то изменения не требуются
        if current_table == new_table_data:
            return 
        
        #В этом блоке происходит добавление в предварительные листы добавления в таблицу и изменения цены
        dict_to_add_in_current_table: Dict[ItemURL, WebsiteItemData] = {}
        dict_to_change_price_in_current_table: Dict[ItemURL, WebsiteItemData] = {}

        for row in new_table_data:
            if new_table_data[row] in current_table.values():
                continue
            if new_table_data[row] not in current_table.values() and row not in list_off_current_table_active_urls and row not in list_off_current_table_not_active_urls:
                dict_to_add_in_current_table[row] = new_table_data[row]
            if new_table_data[row] not in current_table.values() and (row in list_off_current_table_active_urls or row in list_off_current_table_not_active_urls):
                dict_to_change_price_in_current_table[row] = new_table_data[row]

        #В этом блоке добавляем новые строки в текущую таблицу или меняем цену текущих записей
        if dict_to_add_in_current_table:
            await set_data_to_parsed_item_table(current_session, dict_to_add_in_current_table)
        if dict_to_change_price_in_current_table:
            await change_current_price_in_parsed_item_table(current_session, dict_to_change_price_in_current_table)

        #Деактивируем или активируем строки. Деактивация - товар удален с сайта. Активация - товар появился на сайте снова
        await activate_rows_in_parsed_item_table(current_session, current_table, new_table_data, list_off_current_table_not_active_urls)
        await deactivate_rows_in_parsed_item_table(current_session, current_table, new_table_data, list_off_current_table_active_urls)

        await current_session.commit()

async def set_data_to_added_users_item_table(session: async_sessionmaker, data: AddedItemRow) -> None:

    async with session() as session:
        added_item = AddedItem(
            user_name = data.user_name,
            chat_id = data.chat_id,
            item_url = data.item_url,
            shop = data.shop
        )

        session.add(added_item)
        await session.commit()

async def get_query_from_added_users_item_table(session: async_sessionmaker) -> List[AddedItemRow]:
    result = []
    async with session() as current_session:
        rows = select(AddedItem)

        for row in await current_session.scalars(rows):
            row.__dict__.pop('_sa_instance_state')
            row.__dict__.pop('id')
            result.append(AddedItemRow(**row.__dict__))

    return result

async def get_query_from_added_users_item_table_with_username(session: async_sessionmaker, username: str) -> List[AddedItemRow]:
    result = []
    async with session() as current_session:
        rows = select(AddedItem)

        for row in await current_session.scalars(rows):
            if row.__dict__["user_name"] == username:
                row.__dict__.pop("_sa_instance_state")
                row.__dict__.pop("id")
                result.append(AddedItemRow(**row.__dict__))

    return result

async def get_query_from_added_users_item_table_with_list_of_urls(session: AsyncSession, list_of_urls: List[ItemURL]) -> List[AddedItemRow]:
    result: List[AddedItemRow] = []

    rows = select(AddedItem)
    scalars = await session.scalars(rows)
    for row in scalars:
        if ItemURL(row.__dict__['item_url']) in list_of_urls:
            row.__dict__.pop('_sa_instance_state')
            result.append(row.__dict__)

    return result

async def delete_row_from_added_users_item_table(session: AsyncSession, user_name: str, item_url: str, shop: str) -> None:
    async with session() as current_session:
        statement = select(AddedItem).filter_by(user_name=user_name, item_url=item_url, shop=shop)
        objs_to_delete = await current_session.scalars(statement)
        for obj_to_delete in objs_to_delete:
            await current_session.delete(obj_to_delete)
        await current_session.commit()
    