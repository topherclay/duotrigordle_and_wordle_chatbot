# This example requires the 'message_content' intent.

import discord
import parsing_stuff
import os
from dotenv import load_dotenv
import stuff_to_be_saved


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
        name, date = await stuff_to_be_saved.make_class(message.content)
        print(reply)
        await message.channel.send(reply)
        await message.channel.send(f"{name} \n {date}")


client.run(client_token)