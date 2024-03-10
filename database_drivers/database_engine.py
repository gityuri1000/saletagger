from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database_drivers.engine_validation import settings

URI = str(settings.DATABASE_URI).replace("postgresql", "postgresql+asyncpg")
async_engine = create_async_engine(URI, echo=False)

SessionLocal = sessionmaker(bind=async_engine, autoflush=False, autocommit=False, class_=AsyncSession)