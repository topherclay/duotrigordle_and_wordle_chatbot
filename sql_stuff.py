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
    session.close()
    return "This was added to database."


def get_most_recent_board(session):
    result = session.query(GameRow).order_by(sqlalchemy.desc(GameRow.board_number)).first()
    return result.board_number


async def get_all_of_a_day():
    session = Session()
    most_recent_board_number = get_most_recent_board(session=session)

    today_only = session.query(GameRow)\
        .filter(GameRow.board_number == most_recent_board_number)\
        .filter(GameRow.is_a_won_game)\
        .order_by(GameRow.guesses_til_win, GameRow.time)\
        .all()

    result_to_print = ""
    for placement, game in enumerate(today_only):
        result_to_print += repr_a_row(game, placement=placement+1) + "\n"
        print(repr_a_row(game, placement=placement))

    losing_games = session.query(GameRow)\
        .filter(GameRow.board_number == most_recent_board_number)\
        .filter(GameRow.is_a_won_game == False)\
        .order_by(GameRow.guesses_til_win, GameRow.time)\
        .all()

    for game in losing_games:
        result_to_print += repr_a_row(game) + "\n"
        print(repr_a_row(game))


    session.close()
    return result_to_print


def repr_a_row(row, placement="DNQ"):

    user = row.user.split("#")[0]
    if row.is_a_won_game:
        guesses_left = 37 - row.guesses_til_win
    else:
        guesses_left = "None"


    result = f"{str(placement)}: {user}\n" \
             f"{' Guesses left:':<16}{guesses_left:<10}\n" \
             f"{' Total seconds:': <16}{row.time:<10}"
    return result


def get_top():

    session = Session()


    games = session.query(GameRow)\
        .order_by(GameRow.guesses_til_win, GameRow.time)\
        .filter(GameRow.is_a_won_game)\
        .all()


    rank = 1
    result = f"#, {'user':<15} | {'board':<5} | {'seconds':<5}\n"
    for game in games[:10]:
        user = game.user.split("#")[0]
        result += f"{rank}: {user:<15} | {game.board_number:<5} | {game.time:<5} | {game.guesses_til_win} \n"
        rank += 1
    session.close()

    return result