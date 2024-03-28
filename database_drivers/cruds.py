import requests
from typing import List, Dict, Union
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, AsyncSession, async_sessionmaker
from database_drivers.models import Item, AddedItem
from database_drivers.database_engine import async_engine
#
from database_drivers.schemas import ItemInputDict, AddedItemDict
from database_drivers.database_engine import SessionLocal

async def validate_input_data_item_table(data: Dict[str, Dict]) -> None:
    ItemInputDict(data_to_input=data)

async def validate_input_added_users_item_table(data: Dict) -> None:
    AddedItemDict(**data)

async def set_data_to_parsed_item_table(session: AsyncSession, data: Dict[str, Dict]) -> None:
    await validate_input_data_item_table(data=data)

    for row in data.values():
        item = Item(
            item_name = row["item_name"],
            item_url = row["item_url"],
            shop = row["shop"],
            current_price = row["current_price"],
            is_active = row["is_active"]
        )

        session.add(item)

async def change_current_price_in_parsed_item_table(session: AsyncSession, data: Dict[str, Dict]) -> None:
    need_message_urls = []
    await validate_input_data_item_table(data=data)

    for row in data.values():
        stmt = (
            update(Item)
            .where(Item.item_url.in_([row["item_url"]]))
            .values(current_price=row["current_price"])
        )

        need_message_urls.append(row["item_url"])
        await session.execute(stmt)
    
    list_of_need_message_rows = await get_query_from_added_users_item_table_with_list_of_urls(session, need_message_urls)
    
    for row in list_of_need_message_rows:
        requests.get(f"https://api.telegram.org/bot{'6527820749:AAG1xmOjyVtGjsaGlGLu0TBCzXJgAzhdQbM'}/sendMessage?chat_id={row['chat_id']}&text=Изменилась цена на товар: {row['item_url']}&disable_web_page_preview=true")
        
async def get_query_from_parsed_item_table(session: AsyncSession) -> Dict[str, Dict]:
    result = {}

    rows = select(Item)
    scalars = await session.scalars(rows)
    for row in scalars:
        row.__dict__.pop("_sa_instance_state")
        # row.__dict__.pop("id")
        result[row.__dict__["item_url"]] = row.__dict__

    return result

async def deactivate_rows_in_parsed_item_table(
        session: AsyncSession,
        current_table_data: Dict[str, Dict],
        new_table_data: Dict[str, Dict],
        list_of_active_rows: List[str]
        ) -> None:
    # Write func to notify
    await validate_input_data_item_table(data=new_table_data)
    need_message_urls = []

    for row in current_table_data:
        if row not in new_table_data and row in list_of_active_rows:
            stmt = (update(Item)
                .where(Item.item_url == row)
                .values(is_active = 0)
            )

            need_message_urls.append(row)
            await session.execute(stmt)

    list_of_need_message_rows = await get_query_from_added_users_item_table_with_list_of_urls(session, need_message_urls)

    for row in list_of_need_message_rows:
        requests.get(f"https://api.telegram.org/bot{'6527820749:AAG1xmOjyVtGjsaGlGLu0TBCzXJgAzhdQbM'}/sendMessage?chat_id={row['chat_id']}&text=Товар убран из продажи: {row['item_url']}&disable_web_page_preview=true")     

async def activate_rows_in_parsed_item_table(
        session: AsyncSession,
        current_table_data: Dict[str, Dict], 
        new_table_data: Dict[str, Dict], 
        current_not_active_urls_list: List[str]
    ) -> None:
    need_message_urls = []
    await validate_input_data_item_table(data=new_table_data)    

    for row in new_table_data.values():
        if row not in current_table_data.values() and row["item_url"] in current_not_active_urls_list:
            stmt = (update(Item)
                .where(Item.item_url == row["item_url"])
                .values(is_active = 1)
            )

            need_message_urls.append(row["item_url"])
            await session.execute(stmt)

    list_of_need_message_rows = await get_query_from_added_users_item_table_with_list_of_urls(session, need_message_urls)

    for row in list_of_need_message_rows:
        requests.get(f"https://api.telegram.org/bot{'6527820749:AAG1xmOjyVtGjsaGlGLu0TBCzXJgAzhdQbM'}/sendMessage?chat_id={row['chat_id']}&text=Товар снова в продаже: {row['item_url']}&disable_web_page_preview=true")    

async def update_parsed_item_table(session: async_sessionmaker, new_table_data: Dict[str, Dict]) -> None:
    async with session() as current_session:
        #Получаем данные из текущей таблицы, удаляя при этом столбец "id"
        current_table = await get_query_from_parsed_item_table(current_session)

        #Валидируем данные полученные из текущей таблицы
        await validate_input_data_item_table(current_table)

        #Список из URL из текущей таблицы, у которых is_active = 0
        list_off_current_table_not_active_urls: List[str] = [key for key in current_table if current_table[key]["is_active"] == 0]
        #Список из URL из текущей таблицы, у которых is_active = 1
        list_off_current_table_active_urls: List[str] = [key for key in current_table if current_table[key]["is_active"] == 1]
        
        #Если данные из текущей таблицы и новые данные равны, то изменения не требуются
        if current_table == new_table_data:
            return 
        
        #В этом блоке происходит добавление в предварительные листы добавления в таблицу и изменения цены
        dict_to_add_in_current_table: Dict[str, Dict] = {}
        dict_to_change_price_in_current_table: Dict[str, Dict] = {}

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

async def set_data_to_added_users_item_table(session: AsyncSession, data: Dict) -> None:
    await validate_input_added_users_item_table(data=data)

    async with session() as session:
        added_item = AddedItem(
            user_name = data["user_name"],
            chat_id = data["chat_id"],
            item_url = data["item_url"],
            shop = data["shop"]
        )

        session.add(added_item)
        await session.commit()

async def get_query_from_added_users_item_table(session: AsyncSession) -> List[Dict]:
    result = []
    async with session() as current_session:
        rows = select(AddedItem)

        for row in await current_session.scalars(rows):
            row.__dict__.pop('_sa_instance_state')
            result.append(row.__dict__)

    return result

async def get_query_from_added_users_item_table_with_username(session: AsyncSession, username: str) -> List[Dict]:
    result = []
    async with session() as current_session:
        rows = select(AddedItem)

        for row in await current_session.scalars(rows):
            if row.__dict__["user_name"] == username:
                row.__dict__.pop("_sa_instance_state")
                result.append(row.__dict__)

    return result

async def get_query_from_added_users_item_table_with_list_of_urls(session: AsyncSession, list_of_urls: List[str]) -> List[Dict]:
    result = []

    rows = select(AddedItem)
    scalars = await session.scalars(rows)
    for row in scalars:
        if row.__dict__['item_url'] in list_of_urls:
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
    