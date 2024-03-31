import sys
sys.path.append("/home/yyy/Desktop/app_with_git/app")
# Для Docker
sys.path.append("/usr/src/myapp")

import asyncio
from sqlalchemy.ext.asyncio import AsyncEngine
from database_drivers.models import Base
from database_drivers.database_engine import async_engine


async def create_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(create_tables(async_engine))