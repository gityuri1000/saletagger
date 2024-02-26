import asyncio
from typing import List
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, AsyncSession
from database_drivers.models import Item, AddedItem
from database_drivers.database_engine import async_engine

async def set_data_to_parsed_item_table(session: AsyncSession, data: List[dict]) -> None:
    for row in data:
        item = Item(
            item_name = row['item_name'],
            item_url = row['item_url'],
            shop = row['shop'],
            current_price = row['current_price'],
            is_active = row['is_active']
        )

        session.add(item)

async def change_current_price_in_parsed_item_table(session: AsyncSession, data: List[dict]) -> None:
    # Write func to notify

    for row in data:
        stmt = (
            update(Item)
            .where(Item.item_url.in_([row['item_url']]))
            .values(current_price=row['current_price'])
        )
        
        await session.execute(stmt)
        
async def get_query_from_parsed_item_table() -> List[dict]:
    result = []
    async with AsyncSession(async_engine) as current_session:
        rows = select(Item)

        for row in await current_session.scalars(rows):
            row.__dict__.pop('_sa_instance_state')
            result.append(row.__dict__)

    return result

async def deactivate_rows_in_parsed_item_table(session: AsyncSession, current_table_data: List[dict], new_table_data: List[dict]) -> None:
    # Write func to notify

    for row in current_table_data:
        if row not in new_table_data:
            stmt = (await
                update(Item)
                .where(Item.item_url == row['item_url'])
                .values(is_active = False)
            )

            await session.execute(stmt)

async def activate_rows_in_parsed_item_table(session: AsyncSession ,current_table_data: List[dict], new_table_data: List[dict], current_urls_list: List[str]) -> None:
    #Write func to notify

    for row in new_table_data:
        if row not in current_table_data and row['item_url'] in current_urls_list:
            stmt = (await update(Item)
                .where(Item.item_url == row['item_url'])
                .values(is_active = True)
            )

            await session.execute(stmt)



async def update_parsed_item_table(new_table_data: List[dict]) -> None:
    async with AsyncSession(async_engine) as current_session:
        current_table = await get_query_from_parsed_item_table()
        for row in current_table:
            row.pop('id')

        list_off_current_table_urls = [row['item_url'] for row in current_table]
        list_to_add_in_current_table = []
        list_to_change_data_in_current_table = []

        if current_table == new_table_data:
            return
        
        for row in new_table_data:
            if row in current_table:
                continue
            if row not in current_table and row['item_url'] not in list_off_current_table_urls:
                list_to_add_in_current_table.append(row)
            if row not in current_table and row['item_url'] in list_off_current_table_urls:
                list_to_change_data_in_current_table.append(row)

        if list_to_add_in_current_table:
            await set_data_to_parsed_item_table(current_session, list_to_add_in_current_table)
        if list_to_change_data_in_current_table:
            await change_current_price_in_parsed_item_table(current_session, list_to_change_data_in_current_table)

        await deactivate_rows_in_parsed_item_table(current_session, current_table, new_table_data)
        await activate_rows_in_parsed_item_table(current_session, current_table, new_table_data, list_off_current_table_urls)

        await current_session.commit()

async def set_data_to_added_users_item_table(data: dict) -> None:
    async with AsyncSession(async_engine) as session:
        added_item = AddedItem(
            user_name = data['user_name'],
            item_url = data['item_url']
        )

        await session.add(added_item)
        await session.commit()

# def get_query_from_added_users_item_table() -> List[dict]:
#     rows = select(AddedItem)
#     result = []
#     with Session(engine) as current_session:

#         for row in current_session.scalars(rows):
#             row.__dict__.pop('_sa_instance_state')
#             result.append(row.__dict__)

#     return result
    