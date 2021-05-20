from asyncio.windows_events import NULL
import os

import discord
import random
import numpy as np
from discord import channel
from dotenv import load_dotenv
from discord.ext import commands

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
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='bb!', intents=intents)

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


# @client.event
# async def on_ready():
#     guild = discord.utils.get(client.guilds, name=SERVER)
#     print(
#         f'{client.user} is connected to the following guild:\n'
#         f'{guild.name}(id: {guild.id})'
#     )

@bot.command(name='info', help='My info')
async def info(ctx):
    response = INFO_MSG
    await ctx.send(response)

@bot.command(name='annoy', help='Me give u free insults!')
async def annoy(ctx):
    message = ctx.message
    response = "Let me annoy you real quick..."
    await ctx.send(response)
    
    member = message.author
    await member.create_dm()
    await member.dm_channel.send(
    f'Hey {member.name}, {random.choice(ANNOY_MSGS)}')

@bot.command(name='opinion', help="The bot's opinion about something")
async def opinion(ctx):
    message = ctx.message
    interest = message.content[11:]

    if len(interest) == 0:
        response = "Tell me something to give an opinion about?"
    else:
        response = calculate_best_opinion(interest)
    await ctx.send(response)

@bot.command(name='handsome', help="Are you handsome?")
@commands.has_role('Nub Dev')
async def handsome(ctx):
    await ctx.send("Yes, Developers are handsome.")

@bot.command(name='greet', help="Friendly greet a person :D")
async def greet(ctx, user: discord.User=NULL):
    if user == NULL:
        sorted_member_list = sorted(ctx.guild.members, key=lambda x: x.joined_at)
        user = sorted_member_list[-1]
    embed = discord.Embed(
        title = "One of Us! One of Us!",
        color=discord.Colour.purple()
    )
    embed.add_field(name="A NEW PAL!", value= f'We got a new member! <@{user.id}> is here to rockkkk!')
    embed.set_image(url="https://c.tenor.com/ZhAmHufSyFsAAAAM/grand-blue.gif")
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('No no no, testers are lovely, not handsome.')
bot.run(TOKEN)