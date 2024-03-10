import asyncio

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import Integer, String, Boolean, ForeignKey, Null
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Item(Base):
    __tablename__ = 'parsed_item_table'

    id = mapped_column(Integer, primary_key=True)
    item_name = mapped_column(String(255), nullable=False)
    item_url = mapped_column(String(255), nullable=False)
    shop = mapped_column(String(150), nullable=False)
    current_price = mapped_column(Integer, nullable=True)
    is_active = mapped_column(Boolean, nullable=False)

class AddedItem(Base):
    __tablename__ = 'added_users_item_table'
    
    id = mapped_column(Integer, primary_key=True)
    user_name = mapped_column(String(255), nullable=False)
    item_url = mapped_column(String(255), nullable=False)
    shop = mapped_column(String(255), nullable=False)

# Initialize tables if does not exist
if __name__ == "__main__":

    from database_engine import async_engine

    async def create_tables(engine: AsyncEngine) -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(create_tables(async_engine))
        