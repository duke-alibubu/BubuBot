import os

import discord
import random
import numpy as np
from discord import channel
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_BUBUBOT_TOKEN')
SERVER = os.getenv('SERVER_NAME')
INFO_MSG = os.getenv('INFO_MESSAGE')
ANNOY_MSGS = [
        'you ugly bonobo!',
        'you eternal virgin!',
        'are you a sonnovabitch?',
        "big ass mama's boy"
    ]

OPINION_MSGS = [
    'Absolute Ass',
    'Dogshit',
    'OP',
    "That is just broken, right?",
    'Ehh, just OK'
]

def calculate_best_opinion(obj):
    scores = []
    msg1 = obj.lower().replace(" ", "")
    msg1 = ''.join(random.sample(msg1,len(msg1)))
    
    for idx in range(len(OPINION_MSGS)):
        # to lower & strip space
        msg2 = OPINION_MSGS[idx].lower().replace(" ", "")
        
        
        if (len(msg1) > len(msg2)):
            msg1 = msg1[:len(msg2)]
        elif (len(msg1) < len(msg2)):
            msg2 = msg2[:len(msg1)]
        scores.append(lavenshtein_dist(msg1, msg2)/ random.randint(1, 10))

    random.shuffle(scores)
    min_idx = 0
    min = scores[0]
    for index in range(len(scores)):
        score = scores[index]
        if score < min:
            min = score
            min_idx = index
    return OPINION_MSGS[min_idx]


def lavenshtein_dist(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]

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
    elif message.content == 'bubu!annoy':
        response = "Let me annoy you real quick..."
        await message.channel.send(response)
        
        member = message.author
        await member.create_dm()
        await member.dm_channel.send(
        f'Hey {member.name}, {random.choice(ANNOY_MSGS)}'
    )
    elif len(message.content) >= 12 and message.content[:12] == 'bubu!opinion':
        interest = message.content[13:]

        if len(interest) == 0:
            response = "Tell me something to give an opinion about?"
        else:
            response = calculate_best_opinion(interest)
        await message.channel.send(response)

client.run(TOKEN)