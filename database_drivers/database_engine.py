from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from database_drivers.engine_validation import settings

URI = str(settings.DATABASE_URI).replace("postgresql", "postgresql+asyncpg")
async_engine = create_async_engine(URI, echo=False)

SessionLocal = async_sessionmaker(bind=async_engine, autoflush=False, autocommit=False, class_=AsyncSession)