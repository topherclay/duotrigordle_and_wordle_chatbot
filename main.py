import discord
import parsing_stuff
import os
from dotenv import load_dotenv
import stuff_to_be_saved

import sql_stuff

from loguru import logger
import sys


# this stuff has to stay outside the name==main thing in order for the @client wrapper to work.
load_dotenv()
client_token = os.getenv("CLIENT_TOKEN")
intents = discord.Intents.default()
client = discord.Client(intents=intents)
COMMAND_STRING = {
    "top by rank": "!top",
    "top by speed": "!speed",
    "show current day": "!today",
    "show commands": "!help",
    "show top with offset": "!topfrom",
    "show speed with offset": "!speedfrom",
    "show stats": "!statme",
    "show all stats": "!statall"
}


@client.event
async def on_ready():
    logger.info(f"We have logged in to discord as {client.user}")



@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

        return

    if message.content.startswith("$user"):
        content = message.content
        first_line = content.split("\n")[0]
        user = first_line.split(" ")[1]
        score_string = message.content
        await respond_to_score_post(user, score_string, message)
        return

    if message.content.startswith("Daily Duotrigordle"):
        user = message.author
        score_string = message.content
        await respond_to_score_post(user, score_string, message)
        return

    if message.content == COMMAND_STRING["show current day"]:
        result = await sql_stuff.get_all_of_a_day()
        result = parsing_stuff.add_ticks(result)
        await message.channel.send(result)
        return

    if message.content == COMMAND_STRING["top by rank"]:
        result = sql_stuff.get_top()
        result = parsing_stuff.add_ticks(result)
        await message.channel.send(result)
        return

    if message.content == COMMAND_STRING["top by speed"]:
        result = sql_stuff.get_top_speed()
        result = parsing_stuff.add_ticks(result)
        await message.channel.send(result)
        return

    if message.content.startswith(COMMAND_STRING["show top with offset"]):
        offset = 0
        try:
            offset = message.content.split(f'{COMMAND_STRING["show top with offset"]} ')[1]
            offset = int(offset)
        except IndexError:
            await message.channel.send("Oops, please place one space before first rank you wish to see.")
            return
        except ValueError:
            await message.channel.send(f"Sorry, I was unable to parse `{offset}` as a rank.")
            return

        result = sql_stuff.get_top(offset=offset)
        result = parsing_stuff.add_ticks(result)
        await message.channel.send(result)
        return

    if message.content.startswith(COMMAND_STRING["show speed with offset"]):
        offset = 0
        try:
            offset = message.content.split(f'{COMMAND_STRING["show speed with offset"]} ')[1]
            offset = int(offset)
        except IndexError:
            await message.channel.send("Oops, please place one space before first rank you wish to see.")
            return
        except ValueError:
            await message.channel.send(f"Sorry, I was unable to parse `{offset}` as a rank.")
            return

        result = sql_stuff.get_top_speed(offset=offset)
        result = parsing_stuff.add_ticks(result)
        await message.channel.send(result)
        return

    if message.content == COMMAND_STRING["show commands"]:
        await message.channel.send(HELP_MESSAGE)
        return

    if message.content == COMMAND_STRING["show stats"]:
        logger.info(f"{message.author} asked for stats via {COMMAND_STRING['show stats']}.")
        _user = message.author
        _user = str(_user)
        stat_numbers = await sql_stuff.wordle_personal_stats(_user)
        stat_string = await parsing_stuff.turn_wordle_stats_into_percentages(stat_numbers)
        all_shapes, total_games = await sql_stuff.get_all_shapes_from_one_user(_user)
        block_stats = await parsing_stuff.get_block_stats_from_all_shapes(all_shapes, total_games)
        result = stat_string + "\n" + block_stats
        result = parsing_stuff.add_ticks(result)
        await message.channel.send(result)
        logger.info(f"sent this result:\n{result}")


    if message.content == COMMAND_STRING["show all stats"]:
        result = await sql_stuff.stat_all()
        result = parsing_stuff.add_ticks(result)
        await message.channel.send(result)

    if message.content.startswith("Wordle "):
        await respond_to_wordle_post(message.content, message.author, message)

    if message.content == "!test":
        await try_to_read_history(message)



async def respond_to_score_post(user, score_string, message):
    reply = await parsing_stuff.main_parse(score_string)
    game = await stuff_to_be_saved.make_class(score_string)
    game.user = user
    print(str(game))
    await message.channel.send(reply)

    if not game.time:
        await message.channel.send("(No time value was detected. Enable speedrun mode in order to be entered into the database.)")
        return

    commit_result = await sql_stuff.commit_game_to_db(game)

    # try again when an error happens on committing to MySQL.
    if "Err" in commit_result:
        try_again_message = commit_result
        try_again_message += "\n Whoops, I will try to submit this to the database again."
        await message.channel.send(try_again_message)
        commit_result = await sql_stuff.commit_game_to_db(game)

    await message.channel.send(commit_result)



async def respond_to_wordle_post(content, author, message=None):
    wordle = await parsing_stuff.digest_a_wordle_result(content, author)
    logger.info(f"{author} posted this wordle.\n{wordle}")
    is_success = await sql_stuff.commit_wordle_to_db(wordle)
    return is_success



async def try_to_read_history(context):
    print("i will try to read history now.")

    # none will read all.
    amount_of_messages_to_read = None
    messages = await context.channel.history(limit=amount_of_messages_to_read).flatten()

    amount_found = len(messages)
    print(f"found {amount_found} total messages")

    wordle_messages = [message for message in messages if message.content.startswith("Wordle ")]

    amount_of_wordle_only = len(wordle_messages)
    print(f"\tfound {amount_of_wordle_only} wordle messages")

    for index, message in enumerate(wordle_messages):
        content = message.content
        author = message.author

        try:
            is_success = await respond_to_wordle_post(content, author, message)
        except Exception as e:
            print(message.content)
            print(message.author)
            raise e

        if is_success == "This was not added to the database due to a duplicate entry already existing.":
            print(f"\t{index} already existed")
            continue

        if is_success != "This was added to database.":
            print(f"\tfailed and trying again on {index}")
            is_success = await respond_to_wordle_post(content, author, message)

        if is_success == "This was added to database.":
            print(f"\t{index} was a success!")


def generate_help_message():
    def add_ticks(msg):
        return f"```\n{msg}\n```"

    # these have to be very short to avoid wraparound.
    message = "🤖Here are the available commands.🤖\n"
    message += f' {COMMAND_STRING["top by rank"]:<7}: top ten sorted by turns.\n'
    message += f' {COMMAND_STRING["top by speed"]:<7}: top ten sorted by speed.\n'
    message += f' {COMMAND_STRING["show current day"]:<7}: current day\'s board.\n'
    message += f' {COMMAND_STRING["show commands"]:<7}: all commands\n'
    message += f' {COMMAND_STRING["show top with offset"]:<7}: ten ranks starting from a user provided rank.\n'
    message += f' {COMMAND_STRING["show speed with offset"]:<7}: ten ranks starting from a user provided rank, sorted by speed.\n'
    message += f' {COMMAND_STRING["show stats"]:<7}: Your wordle stats.\n'
    message += f' {COMMAND_STRING["show all stats"]:<7}: All gordle stats.\n'
    message = add_ticks(message)

    for command_key, command in COMMAND_STRING.items():
        assert command in message, f"{command} does not have a !help description!"

    return message


def set_up_logger():
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    logger.add("gordle_logs.log", rotation="1 day", retention="7 days")







if __name__ == "__main__":
    set_up_logger()
    HELP_MESSAGE = generate_help_message()
    client.run(client_token)

