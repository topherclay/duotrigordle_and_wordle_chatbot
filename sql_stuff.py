from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

SQL_URI = os.getenv("SQLALCHEMY_DATABASE_URI")

engine = create_engine(SQL_URI, echo=True)
# connection = engine.connect()

print(engine.table_names())


async def print_tables():
    connection = engine.connect()
    print(connection)
    print(engine.get_tables())
