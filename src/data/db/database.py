from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel, text

from data.db.config import settings

# Motor asíncrono usando las settings
engine = create_async_engine(
    settings.database_url,
    echo=True,  # Log de queries (como logger.Info en GORM)
    pool_size=10,
    max_overflow=5,
)

# Session maker (equivalente a obtener una conexión del pool)
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Crea las tablas y extensión pgvector (equivalente a AutoMigrate de GORM)"""
    async with engine.begin() as conn:
        # Crear extensión pgvector
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        # Crear todas las tablas
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency para FastAPI con manejo de errores profesional"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
