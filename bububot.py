import os

import discord
import random
from discord import channel
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_BUBUBOT_TOKEN')
SERVER = os.getenv('SERVER_NAME')
INFO_MSG = os.getenv('INFO_MESSAGE')
ANNOY_MSGS = [
        'you ugly bonobo!',
        'you eternal virgin!',
        "are you Fireball's GF?"
    ]

client = discord.Client()

@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=SERVER)
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@client.event
async def on_message(message):
    # don't reply to the bot itself
    if message.author == client.user:
        return
    
    if message.content == 'bubu!info':
        response = INFO_MSG
        await message.channel.send(response)
    
    if message.content == 'bubu!annoy':
        response = "Let me annoy you real quick..."
        await message.channel.send(response)
        
        member = message.author
        await member.create_dm()
        await member.dm_channel.send(
        f'Hey {member.name}, {random.choice(ANNOY_MSGS)}'
    )



client.run(TOKEN)