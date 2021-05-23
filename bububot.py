from asyncio.windows_events import NULL
import os

import discord
import random
from discord.ext.commands import errors
import numpy as np
import pyrebase
from discord import channel
from dotenv import load_dotenv
from discord.ext import commands
from datetime import datetime, timedelta
from discord.utils import get
from random import randrange

load_dotenv()
TOKEN = os.getenv('DISCORD_BUBUBOT_TOKEN')
SERVER = os.getenv('SERVER_NAME')
INFO_MSG = os.getenv('INFO_MESSAGE')

#firebase auth info
firebase_apiKey = os.getenv('firebase_apiKey')
firebase_authDomain = os.getenv('firebase_authDomain')
firebase_projectId = os.getenv('firebase_projectId')
firebase_storageBucket = os.getenv('firebase_storageBucket')
firebase_messagingSenderId = os.getenv('firebase_messagingSenderId')
firebase_appId = os.getenv('firebase_appId')
firebase_measurementId = os.getenv('firebase_measurementId')
firebase_dbURL = os.getenv('firebase_dbURL')

firebase_config = {
    "apiKey": firebase_apiKey,
    "authDomain": firebase_authDomain,
    "projectId": firebase_projectId,
    "storageBucket": firebase_storageBucket,
    "messagingSenderId": firebase_messagingSenderId,
    "appId": firebase_appId,
    "measurementId": firebase_measurementId,
    "databaseURL": firebase_dbURL
}

firebase = pyrebase.initialize_app(firebase_config)
storage = firebase.storage()

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
async def greet(ctx, user: discord.User=None):
    if user is None:
        # if the user is not specified, latest-joined user will be tagged
        sorted_member_list = sorted(ctx.guild.members, key=lambda x: x.joined_at)
        user = sorted_member_list[-1]
    else:
        user = [x for x in ctx.guild.members if x.id == user.id][0]
    
    # check if the user has join more than 1 day
    now = datetime.now()
    difference = now - user.joined_at
    if (difference <= timedelta(days=1)):
        response = (
            "**One of Us! One of Us!**\n" +
            "**A NEW PAL!**\n" + 
            f'We got a new member! <@{user.id}> is here to rockkkk!\n'+
            "https://gfycat.com/welldocumentedevilamethystsunbird-bogdee"
        )
    else:
        response = (
            "**A fellow PAB veteran!**\n" +
            "**A VETERAN!**\n" + 
            f'<@{user.id}>, I hope you have a nice day with lots of alcohol!\n'+
            "https://tenor.com/view/grand-blue-cheers-beer-party-anime-gif-16490634"
        )
    await ctx.send(response)

@bot.command(name='roleping', help="A person with a given role pings all the people with that role")
async def roleping(ctx):
    message = ctx.message
    role = message.content[12:].lstrip()

    if role is None:
        await ctx.send("Sorry pal, please specify the role name for me to ping!")
        return
    
    searched_role = get(ctx.guild.roles, name=role)
    if searched_role is None:
        await ctx.send("Sorry pal, you specified a wrong role name :(")
        return
    
    sender = ctx.author
    if searched_role in sender.roles:
        await ctx.send(f'Hello {searched_role.mention}, <@{sender.id}> wants to ping you to do something hideous!')
    else:
        await ctx.send(f'Sorry pal, you do not have the role {role} :(')

@bot.command(name='ass', help="Display an ass.")
async def ass(ctx):
    if not ctx.channel.is_nsfw():
        await ctx.send("Sorry pal, you can only use this command in a NSFW channel.")
        return
    MAX = 8
    img_path = f'ass/{randrange(MAX) + 1}.jpg'
    img_url = storage.child(img_path).get_url(None)
    await ctx.send("Ah I see, you are a man of culture as well.")
    await ctx.send(img_url)

@bot.command(name='blush', help="Ya make me blush")
async def blush(ctx):
    MAX = 13
    img_path = f'blush/{randrange(MAX) + 1}.jpg'
    img_url = storage.child(img_path).get_url(None)
    await ctx.send("B... Baka!")
    await ctx.send(img_url)

@bot.command(name='quote', help="Quote a sent message")
async def blush(ctx, msg_id: int = None, channel: discord.TextChannel=None):
    if msg_id is None:
        await ctx.send("Please specify a message ID")
        return
    if channel is None:
        channel = ctx.channel
    msg = await channel.fetch_message(msg_id)
    embed = discord.Embed(
        title = f'Message from {msg.author.name}',
        color=discord.Colour.purple()
    )

    embed.add_field(name="Author", value =  f'<@{msg.author.id}>')

    is_censored = channel.id != ctx.channel.id and (channel.is_nsfw or 'spoiler' in channel.name)
    if is_censored:
        embed.add_field(name="said: ", value =  f"||{msg.content}||")
    else:
        embed.add_field(name="said: ", value =  msg.content)
    
    embed.set_thumbnail(url=msg.author.avatar_url)
    embed.description = f'[Jump to the message]({msg.jump_url})'
    embed.set_footer(text=f'Sent at at {msg.created_at.strftime("%m/%d/%Y, %H:%M:%S")} in #{msg.channel.name}')

    await ctx.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    print(type(error))
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('No no no, testers are lovely, not handsome.')
    elif isinstance(error, commands.errors.ChannelNotFound):
        await ctx.send('Channel name is wrong, or you do not need the permission to read messages in this channel :(')
    elif isinstance(error, commands.errors.CommandInvokeError):
        original = error.original
        if isinstance(original, discord.errors.NotFound):
            await ctx.send('No message with such ID exists. Please check it again my friend :<')


bot.run(TOKEN)