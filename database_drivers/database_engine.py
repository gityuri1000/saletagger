from sqlalchemy.ext.asyncio import create_async_engine

async_engine = create_async_engine("postgresql+asyncpg://postgres:123@localhost:5432/saletagger", echo=False)