# This example requires the 'message_content' intent.

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




    if "Daily Duotrigordle" in message.content:
        reply = await parsing_stuff.main_parse(message.content)
        game = await stuff_to_be_saved.make_class(message.content)
        game.user = str(message.author)
        print(str(game))
        await message.channel.send(reply)
        await message.channel.send(str(game))
        commit_result = await sql_stuff.commit_game_to_db(game)
        await message.channel.send(commit_result)



client.run(client_token)