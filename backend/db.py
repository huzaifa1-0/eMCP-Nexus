import databases
import sqlalchemy
from backend.config import settings

DATABASE_URL = settings.DATABASE_URL

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)


async def init_db():
    await database.connect()