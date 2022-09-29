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


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
        await sql_stuff.get_all_of_a_day()

    if message.content.startswith("$user"):
        content = message.content
        first_line = content.split("\n")[0]
        user = first_line.split(" ")[1]
        score_string = message.content
        await respond_to_score_post(user, score_string, message)

    if message.content.startswith("Daily Duotrigordle"):
        user = message.author
        score_string = message.content
        await respond_to_score_post(user, score_string, message)

    if message.content == "!today":
        result = await sql_stuff.get_all_of_a_day()
        result = parsing_stuff.add_ticks(result)
        await message.channel.send(result)

    if message.content == "!top":
        result = sql_stuff.get_top()
        result = parsing_stuff.add_ticks(result)
        await message.channel.send(result)

    if message.content == "!speed":
        result = sql_stuff.get_top_speed()
        result = parsing_stuff.add_ticks(result)
        await message.channel.send(result)


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
    if "err" in commit_result:
        try_again_message = commit_result
        try_again_message += "\n Whoops, I will try to submit this to the database again."
        await message.channel.send(try_again_message)
        commit_result = await sql_stuff.commit_game_to_db(game)

    await message.channel.send(commit_result)





client.run(client_token)