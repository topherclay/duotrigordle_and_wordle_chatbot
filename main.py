import discord
import parsing_stuff
import os
from dotenv import load_dotenv
import stuff_to_be_saved

import sql_stuff


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
    print(f'We have logged in as {client.user}')


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
        _user = message.author
        _user = str(_user)
        result = await sql_stuff.stat_me(_user)
        result = parsing_stuff.add_ticks(result)
        await message.channel.send(result)

    if message.content == COMMAND_STRING["show all stats"]:
        result = await sql_stuff.stat_all()
        result = parsing_stuff.add_ticks(result)
        await message.channel.send(result)

    if message.content.startswith("Wordle "):
        await respond_to_wordle_post(message.content, message.author)

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



async def respond_to_wordle_post(content, author):
    wordle = await parsing_stuff.digest_a_wordle_result(content, author)
    print(wordle)

    is_success = await sql_stuff.commit_wordle_to_db(wordle)

    return is_success



async def try_to_read_history(context):
    print("i will try to read history now.")

    messages = await context.channel.history(limit=None).flatten()

    amount_found = len(messages)
    print(f"found {amount_found} total messages")

    wordle_messages = [message for message in messages if message.content.startswith("Wordle ")]

    amount_of_wordle_only = len(wordle_messages)
    print(f"found {amount_of_wordle_only} wordle messages")

    for index, message in enumerate(wordle_messages):
        content = message.content
        author = message.author

        is_success = await respond_to_wordle_post(content, author)

        if is_success != "This was added to database.":
            print(f"failed and trying again on {index}")
            is_success = await respond_to_wordle_post(content, author)

        if is_success == "This was added to database.":
            print(f"{index} was a success!")


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
    message += f' {COMMAND_STRING["show stats"]:<7}: Your stats.\n'
    message += f' {COMMAND_STRING["show all stats"]:<7}: All stats.\n'
    message = add_ticks(message)

    for command_key, command in COMMAND_STRING.items():
        assert command in message, f"{command} does not have a !help description!"

    return message


HELP_MESSAGE = generate_help_message()
client.run(client_token)