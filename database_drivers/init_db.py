import sys
sys.path.append("/home/yyy/Desktop/app_with_git/app")

import asyncio
from sqlalchemy.ext.asyncio import AsyncEngine
from database_drivers.models import Base
from database_drivers.database_engine import async_engine


if __name__ == "__main__":

    async def create_tables(engine: AsyncEngine) -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(create_tables(async_engine))