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

engine = create_engine(SQL_URI, echo=False)
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
    """This is really only for the `!today` command output."""
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

    if offset:
        result = f"🏆Ten ranks starting from {offset}🏆\n"

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

    if offset:
        result = f"⏱Ten ranks starting from {offset}⏱\n"

    result += create_rank_table(games, offset=offset)

    session.close()

    return result


def create_rank_table(games, offset):
    # to make the user supplied number match rank.
    if offset:
        offset -= 1

    rank = offset+1
    result = f"{'#':>2}: {'user':^12}|{'day':^3}|{'time':^8}|{'ts':^2}\n"
    for game in games[offset:offset+10]:
        user = game.user.split("#")[0]
        time = parsing_stuff.convert_seconds_to_formatted_string(game.time)
        result += f"{rank:>2}: {user:<12}|{game.board_number:^3}|{time:^8}|{game.guesses_til_win:^2} \n"
        rank += 1
    return result


def get_user_from_string(user):
    found_user = None
    session = Session()
    users = session.query(GameRow.user).distinct().all()
    for name in users:
        if user.lower() in name[0].lower():
            found_user = name[0]
            break

    return found_user


def get_streak_from_username(_username, winning=True):
    user = str(_username)
    session = Session()

    query_results = session.query(GameRow) \
        .filter(GameRow.user == _username) \
        .filter(GameRow.is_a_won_game == winning) \
        .order_by(GameRow.board_number) \
        .all()

    current_streak = 0
    highest_streak = 0
    starting_day = None
    best_start = None
    ending_day = None
    best_end = None

    current_check = None

    for game in query_results:

        if not starting_day:
            starting_day = game.board_number
            current_check = starting_day + 1
            ending_day = starting_day
            current_streak = 1


        if current_check == game.board_number:
            ending_day = game.board_number
            current_streak += 1
            current_check += 1
        else:
            starting_day = game.board_number
            current_streak = 1
            ending_day = starting_day
            current_check = starting_day + 1

        if current_streak > highest_streak:
            highest_streak = current_streak
            best_start = starting_day
            best_end = ending_day

    user = user.split("#")[0]
    win_lose = "win" if winning else "lose"
    result = f"{user}'s longest {win_lose} streak is {highest_streak} days, from {best_start} to {best_end}"
    return result, highest_streak


def get_all_usernames():
    session = Session()
    users = session.query(GameRow.user).distinct().all()

    usernames = [user[0] for user in users]

    return usernames



def all_personal_stats(_username):
    user = _username
    """
    count of games played .
    streak of games played .
    count of wins .
    longest win streak .
    count of loses .
    presumed count of losses with missing games .....
    longest lose streak .
    percentage of wins to losses  
    percentage of wins to presumed losses.
    count of wins of the day's competition
    streaks of winning the day's competition
    """

    session = Session()
    count_of_games_played = session.query(GameRow) \
        .filter(GameRow.user == user).all()

    count_of_games_played = len(count_of_games_played)
    print(f"{user} played {count_of_games_played} games")

    presumed_count = session.query(GameRow.board_number)\
        .filter(GameRow.user == user) \
        .order_by(sqlalchemy.asc(GameRow.board_number)).all()

    presumed_count = presumed_count[-1][0] - presumed_count[0][0] + 1
    print(f"{user} should have {presumed_count} games.")


    streak_of_games_played = get_streak_from_username(user, winning=True)
    print(f"{user} longest winning streak is {streak_of_games_played[1]} games.")

    lose_streak = get_streak_from_username(user, winning=False)
    print(f"{user} longest losing streak is {lose_streak[1]} games.")

    count_of_wins = session.query(GameRow) \
        .filter(GameRow.user == user)\
        .filter(GameRow.is_a_won_game == True)\
        .all()
    count_of_wins = len(count_of_wins)
    print(f"{user} won {count_of_wins} total.")


    count_of_losses = session.query(GameRow) \
        .filter(GameRow.user == user)\
        .filter(GameRow.is_a_won_game == False)\
        .all()
    count_of_losses = len(count_of_losses)
    presumed_losses = presumed_count - count_of_wins - count_of_losses
    print(f"{user} lost {count_of_losses} total. (+{presumed_losses} losses.)")


    percentage_wins = (count_of_wins / (count_of_wins + count_of_losses)) * 100
    percentage_wins = round(percentage_wins, 2)
    presumed_percentage_wins = (count_of_wins / (count_of_wins + count_of_losses + presumed_losses)) * 100
    presumed_percentage_wins = round(presumed_percentage_wins, 2)
    print(f"{user} won {percentage_wins:02.02f}% ({presumed_percentage_wins:02.02f}%).")


    percentage_lost = count_of_losses / (count_of_wins + count_of_losses) * 100
    percentage_lost = round(percentage_lost, 2)
    presumed_percentage_lost = (count_of_losses + presumed_losses) / (count_of_wins + count_of_losses + presumed_losses) * 100
    presumed_percentage_lost = round(presumed_percentage_lost, 2)
    print(f"{user} lost {percentage_lost:02.02f}% ({presumed_percentage_lost:02.02f}%).")


    result = {"count_of_games": count_of_games_played,
               "presumed_games_played": presumed_count,
               "win_streak": streak_of_games_played[1],
               "lose_streak": lose_streak[1],
               "win_total": count_of_wins,
               "lose_total": count_of_losses,
               "presumed_loses": presumed_losses,
               "presumed_win_percentage": presumed_percentage_wins,
               "presumed_lose_percentage": presumed_percentage_lost,
               "percentage_wins":  percentage_wins,
               "percentage_lost": percentage_lost,
               "user": user}

    return result


def display_one_stat_block(which_single_user):

    # result = {"count_of_games": count_of_games_played,
    #            "presumed_games_played": presumed_count,
    #            "win_streak": streak_of_games_played,
    #            "lose_streak": lose_streak,
    #            "win_total": count_of_wins,
    #            "lose_total": count_of_losses,
    #            "presumed_loses": presumed_losses,
    #            "presumed_win_percentage": presumed_percentage_wins,
    #            "presumed_lose_percentage": presumed_percentage_lost,
    #            "percentage_wins":  percentage_wins,
    #            "percentage_lost": percentage_lost,
    #            "user": user}



    try:
        stats: dict = all_personal_stats(which_single_user)
    except Exception as e:
        print(e)
        print(which_single_user)
        return e




    full_string = f"Stats for {stats['user']}:\n" \
                  f"\tTotal Games: {stats['count_of_games']} ({stats['presumed_games_played']})\n" \
                  f"\tWins: {stats['win_total']}\n" \
                  f"\tLosses: {stats['lose_total']} (+{stats['presumed_loses']})\n" \
                  f"\tW%: {stats['percentage_wins']}% ({stats['presumed_win_percentage']}%)\n" \
                  f"\tL%: {stats['percentage_lost']}% ({stats['presumed_lose_percentage']}%)\n" \
                  f"\tWin Streak: {stats['win_streak']}\n" \
                  f"\tLose Streak: {stats['lose_streak']}"\
                  f"\t"


    return full_string


async def stat_me(_username):
    return display_one_stat_block(_username)





if __name__ == "__main__":
    print("testing")

    username = get_user_from_string("lark")

    display_one_stat_block(username)

    # user_stats = []
    # for name in get_all_usernames():
    #     user_stats.append(all_personal_stats(name))






