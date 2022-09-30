import sqlalchemy.exc
from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, Boolean, Float, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

import os
from dotenv import load_dotenv

import parsing_stuff
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
    resulting_string = ""
    try:
        to_be_added = GameRow(user=game.user,
                              is_a_won_game=game.is_a_won_game,
                              guesses_til_win=game.guesses_til_win,
                              time=game.time_as_seconds,
                              board_number=int(game.board_number))

        session.add(to_be_added)
        session.commit()
        resulting_string = "This was added to database."
    except sqlalchemy.exc.IntegrityError:
        resulting_string = "This was not added to the database due to a duplicate entry already existing."
    except Exception as e:
        print(e)
        resulting_string = str(type(e))
    session.close()

    return resulting_string


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

    result_to_print = "🌞Games from today.🌞\n"
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
        guesses_left = row.guesses_til_win
    else:
        guesses_left = "DNQ"

    time = parsing_stuff.convert_seconds_to_formatted_string(row.time)

    result = f"{str(placement)}: {user}\n" \
             f"{' Turns used:':>13} {guesses_left:<3}\n" \
             f"{' Time used:': >13} {time:<8}"
    return result


def get_top(offset=0):
    session = Session()
    games = session.query(GameRow)\
        .order_by(GameRow.guesses_til_win, GameRow.time)\
        .filter(GameRow.is_a_won_game)\
        .all()

    result = "🏆Top ten by turns used.🏆\n"
    result += create_rank_table(games, offset=offset)

    session.close()

    return result


def get_top_speed(offset=0):
    session = Session()
    games = session.query(GameRow)\
        .order_by(GameRow.time)\
        .filter(GameRow.is_a_won_game)\
        .all()

    result = "⏱Top ten by speed.⏱\n"
    result += create_rank_table(games, offset=offset)

    session.close()

    return result


def create_rank_table(games, offset):
    rank = offset+1
    result = f"{'#':>2}: {'user':^12}|{'day':^3}|{'time':^8}|{'ts':^2}\n"
    for game in games[offset:10]:
        user = game.user.split("#")[0]
        time = parsing_stuff.convert_seconds_to_formatted_string(game.time)
        result += f"{rank:>2}: {user:<12}|{game.board_number:^3}|{time:^8}|{game.guesses_til_win:^2} \n"
        rank += 1
    return result