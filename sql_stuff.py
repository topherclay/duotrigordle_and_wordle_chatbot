import sqlalchemy.exc
from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, Boolean, Float, UniqueConstraint
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
    board_number = Column(Integer)
    UniqueConstraint(user, board_number, name="one_per_day")



Base.metadata.create_all(engine)


async def commit_game_to_db(game: SingleGame):
    session = Session()

    try:
        to_be_added = GameRow(user=game.user,
                              is_a_won_game=game.is_a_won_game,
                              guesses_til_win=game.guesses_til_win,
                              time=game.time_as_seconds,
                              board_number=int(game.board_number))

        session.add(to_be_added)
        session.commit()
    except sqlalchemy.exc.IntegrityError:
        return "This was not added to the database due to a duplicate entry already existing."

    return "This was added to database."


def get_most_recent_board(session):
    result = session.query(GameRow).order_by(sqlalchemy.desc(GameRow.board_number)).first()
    return result.board_number


async def get_all_of_a_day():
    session = Session()
    most_recent_board_number = get_most_recent_board(session=session)

    today_only = session.query(GameRow)\
        .filter(GameRow.board_number == most_recent_board_number)\
        .order_by(GameRow.guesses_til_win, GameRow.time)\
        .all()

    result_to_print = ""
    for game in today_only:
        result_to_print += repr_a_row(game) + "\n"
        print(repr_a_row(game))

    return result_to_print


def repr_a_row(row):

    user = row.user.split("#")[0]
    guesses_left = 37 - row.guesses_til_win

    result = f"{user}\n" \
             f"{' Guesses to spare:':<20}{guesses_left:<10}\n" \
             f"{' Total seconds:': <20}{row.time:<10}"
    return result

