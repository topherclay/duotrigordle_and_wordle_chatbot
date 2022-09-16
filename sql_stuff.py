from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

import os
from dotenv import load_dotenv

Base = declarative_base()

load_dotenv()
SQL_URI = os.getenv("SQLALCHEMY_DATABASE_URI")

engine = create_engine(SQL_URI, echo=True)


class GameRow(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True)
    user = Column(String(64))
    is_a_won_game = Column(Boolean)
    guesses_til_win = Column(Integer)
    time_til_win = Column(String(32))



Base.metadata.create_all(engine)






async def print_tables():
    connection = engine.connect()
    print(connection)
    print(engine.table_names())
