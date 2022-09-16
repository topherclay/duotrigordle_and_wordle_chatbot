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
        await sql_stuff.print_tables()



    if "Daily Duotrigordle" in message.content:
        reply = await parsing_stuff.main_parse(message.content)
        game = await stuff_to_be_saved.make_class(message.content)
        game.user = str(message.author)
        print(str(game))
        await message.channel.send(reply)
        await message.channel.send(str(game))
        print(game.turn_time_to_seconds())


client.run(client_token)