from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

import os
from dotenv import load_dotenv
from stuff_to_be_saved import SingleGame


Base = declarative_base()

load_dotenv()
SQL_URI = os.getenv("SQLALCHEMY_DATABASE_URI")

engine = create_engine(SQL_URI, echo=True)
Session = sessionmaker(bind=engine)

class GameRow(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True)
    user = Column(String(64))
    is_a_won_game = Column(Boolean)
    guesses_til_win = Column(Integer)
    time = Column(Float)
    board_numer = Column(Integer)



Base.metadata.create_all(engine)


async def commit_game_to_db(game: SingleGame):
    session = Session()

    to_be_added = GameRow(user=game.user,
                          is_a_won_game=game.is_a_won_game,
                          guesses_til_win=game.guesses_til_win,
                          time=game.time_as_seconds,
                          board_number=int(game.board_number))

    session.add(to_be_added)
    session.commit()
    return "Added"


async def print_tables():
    connection = engine.connect()
    print(connection)
    print(engine.table_names())
