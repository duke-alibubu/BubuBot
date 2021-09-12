import os

import discord
import random
from discord.ext.commands import errors
from discord.ext.commands.core import has_permissions
import numpy as np
import pyrebase
from discord import channel
from dotenv import load_dotenv
from discord.ext import commands
from datetime import datetime, timedelta
from discord.utils import get
from random import randrange
from discord.utils import find
import requests
from bs4 import BeautifulSoup

load_dotenv()
TOKEN = os.getenv('DISCORD_BUBUBOT_TOKEN')
SERVER = os.getenv('SERVER_NAME')
AUTHOR_ID = os.getenv('BUBU_DISCORD_ID')

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
db = firebase.database()

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
    'Ehh, just OK',
    'Omega Cringe',
    'Good Stuff',
]
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=['bb!', 'Bb!', 'BB!', 'bB!', 'pab!', 'Pab!', 'PAB!'], intents=intents)

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


@bot.command(name='annoy', help='Me give u free insults! Just type bb!annoy and enjoy the mockery.')
async def annoy(ctx):
    message = ctx.message
    response = "Let me annoy you real quick..."
    await ctx.send(response)
    
    member = message.author
    await member.create_dm()
    await member.dm_channel.send(
    f'Hey {member.name}, {random.choice(ANNOY_MSGS)}')

@bot.command(help="Aliases: op. The bot's opinion about something. bb!opinion [something] is the format!")
async def opinion(ctx):
    message = ctx.message
    interest = message.content[11:]

    if len(interest) == 0:
        response = "Tell me something to give an opinion about?"
    else:
        response = calculate_best_opinion(interest)
    await ctx.send(response)

@bot.command(name='greet', help="Friendly greet a person. bb!greet [user_id] to greet them. if user_id is not specified, latest-joined user will be greeted.")
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

@bot.command(name='roleping', help="Aliases: rp. A person with a given role pings all the people with that role. bb!roleping [role_name] is how you do it!")
async def roleping(ctx):
    guild = ctx.guild
    if guild is None:
        await ctx.send(f'An error occurred and this server is no longer in my database. Please contact the creator <@{AUTHOR_ID}> for help regarding this matter.')
        return

    message = ctx.message
    role = message.content[12:].lstrip()

    if role is None:
        await ctx.send("Sorry pal, please specify the role name for me to ping!")
        return
    
    searched_role = get(ctx.guild.roles, name=role)
    if searched_role is None:
        await ctx.send("Sorry pal, you specified a wrong role name :(")
        return
    
    pingable_roles = db.child("guilds").child(guild.id).child("pingable_roles").get().val()
    if pingable_roles is None:
        await ctx.send(f'Sorry pal, this role is not pingable.\nCurrently no roles have been added to the pingable lists, call an admin to do it!')
        return
    elif not role in pingable_roles.keys():
        await ctx.send(f'Sorry pal, this role is not pingable.')
        return

    sender = ctx.author
    if searched_role in sender.roles:
        await ctx.send(f'Hello {searched_role.mention}, <@{sender.id}> wants to ping you to do something hideous!')
    else:
        await ctx.send(f'Sorry pal, you do not have the role {role} :(')

@bot.command(name='rp', help="Aliases: roleping. A person with a given role pings all the people with that role. bb!roleping [role_name] is how you do it!")
async def roleping_rp(ctx):
    guild = ctx.guild
    if guild is None:
        await ctx.send(f'An error occurred and this server is no longer in my database. Please contact the creator <@{AUTHOR_ID}> for help regarding this matter.')
        return

    message = ctx.message
    role = message.content[6:].lstrip()

    if role is None:
        await ctx.send("Sorry pal, please specify the role name for me to ping!")
        return
    
    searched_role = get(ctx.guild.roles, name=role)
    if searched_role is None:
        await ctx.send("Sorry pal, you specified a wrong role name :(")
        return
    
    pingable_roles = db.child("guilds").child(guild.id).child("pingable_roles").get().val()
    if pingable_roles is None:
        await ctx.send(f'Sorry pal, this role is not pingable.\nCurrently no roles have been added to the pingable lists, call an admin to do it!')
        return
    elif not role in pingable_roles.keys():
        await ctx.send(f'Sorry pal, this role is not pingable.')
        return

    sender = ctx.author
    if searched_role in sender.roles:
        await ctx.send(f'Hello {searched_role.mention}, <@{sender.id}> wants to ping you to do something hideous!')
    else:
        await ctx.send(f'Sorry pal, you do not have the role {role} :(')

@bot.command(aliases=['butt'], help="Aliases: butt. Display an ass. bb!ass and enjoy the lewdness.")
async def ass(ctx):
    if not ctx.channel.is_nsfw():
        await ctx.send("Sorry pal, you can only use this command in a NSFW channel.")
        return
    MAX = 19
    img_path = f'ass/{randrange(MAX) + 1}.jpg'
    img_url = storage.child(img_path).get_url(None)
    await ctx.send("Ah I see, you are a man of culture as well.")
    await ctx.send(img_url)

@bot.command(aliases=['boobs'], help="Aliases: boobs. Display a pair of tits. bb!tits and enjoy the lewdness.")
async def tits(ctx):
    if not ctx.channel.is_nsfw():
        await ctx.send("Sorry pal, you can only use this command in a NSFW channel.")
        return
    MAX = 26
    img_path = f'tits/{randrange(MAX) + 1}.jpg'
    img_url = storage.child(img_path).get_url(None)
    await ctx.send("Remember: In the end, Boobs - are nothing more than fake asses.")
    await ctx.send(img_url)

@bot.command(name='blush', help="Ya make me blush. bb!blush and enjoy the cuteness.")
async def blush(ctx):
    MAX = 15
    img_path = f'blush/{randrange(MAX) + 1}.jpg'
    img_url = storage.child(img_path).get_url(None)
    await ctx.send("B... Baka!")
    await ctx.send(img_url)

@bot.command(name='hpbd', help="Happy birthday to an user. bb!hpbd to congratulate them.")
async def hpbd(ctx, user: discord.User=None):
    if user is None:
        await ctx.send("Please select the birthday boy/girl so that I can congratulate them!")
        return
    else:
        user = [x for x in ctx.guild.members if x.id == user.id][0]
    MAX = 3
    num = randrange(MAX) + 1

    img_path = f'hpbd/{num}.jpg'
    img_url = storage.child(img_path).get_url(None)
    if num == 1:
        await ctx.send(f'Happy birthday dear <@{user.id}>, want me to give you a smooch?')
    elif num == 2:
        await ctx.send(f'Happy belated birthday <@{user.id}>, I hope you enjoy today as much as I enjoy diving.')
    elif num == 3:
        await ctx.send(f'Ehehehe we have a birthday <@{user.id}> here! Come come let us celebrate ~~')
    await ctx.send(img_url)

@bot.command(aliases=['godnat', 'gudnite', 'gn'], help="Aliases: godnat, gudnite, gn. Says good night. bb!gn is da wei.")
async def goodnight(ctx):
    img_path = 'gn.jpeg'
    img_url = storage.child(img_path).get_url(None)
    await ctx.send("Good night and have a sweet dream there <3")
    await ctx.send(img_url)

@bot.command(aliases=['q', 'quote'], help="Aliases: q, quote.Quote a sent message. bb!quote [message_id] #[channel_name] is the format. If [channel_name] is not specified, the bot will look up in the current channel by default.")
async def quotes(ctx, msg_id: int = None, channel: discord.TextChannel=None):
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

    is_censored = (channel.id != ctx.channel.id) and (channel.is_nsfw() or 'spoiler' in channel.name)
    if len(msg.content) > 0:
        if len(msg.content) > 1024:
            quoted_value = f'{msg.content[:1020]}...'
        else:
            if is_censored:
                quoted_value = f"||{msg.content}||"
            else:
                quoted_value = msg.content
        embed.insert_field_at(1, name="said: ", value = quoted_value, inline=False)

    if len(msg.attachments) > 0:
        if msg.attachments[0].is_spoiler:
            embed.insert_field_at(3, name="SPOILER/NSFW", value = "This image is hidden since it contains spoiler or NSFW contents.", inline=False)
        else:
            embed.set_image(url=msg.attachments[0].proxy_url)
    
    if len(msg.embeds) > 0:
        if is_censored:
            embed.insert_field_at(3, name="SPOILER/NSFW", value = "This image is hidden since it contains spoiler or NSFW contents.", inline=False)
        else:
            embed.set_image(url=msg.embeds[0].image.url)

    embed.set_thumbnail(url=msg.author.avatar_url)
    embed.insert_field_at(2, name="Link", value=f'[Jump to the message]({msg.jump_url})', inline=False)
    embed.set_footer(text=f'Message sent at at {msg.created_at.strftime("%m/%d/%Y, %H:%M:%S")} UTC in #{msg.channel.name}')
    await ctx.send(embed=embed)

@bot.command(name='about', help='My info & acknowledgement')
async def about(ctx):
    embed = discord.Embed(
        title = f'BubuBot by Alibubu',
        color=discord.Colour.dark_blue()
    )
    creator = await bot.fetch_user(AUTHOR_ID)

    embed.insert_field_at(0, name="Creator", value =  f'<@{AUTHOR_ID}>', inline=False)
    embed.insert_field_at(1, name="GitHub Link", value = "https://github.com/duke-alibubu/BubuBot", inline=False)
    embed.insert_field_at(2, name="About me", value = "Born from the creator's idea to try out a Discord bot during his last summer holiday.\nThis is a product made for passion instead of monetization purpose, so the author hopes that users enjoy trying it as well as having the tolerance for the bot =)", inline=False)
    embed.insert_field_at(3, name="What Can I Do", value = "Some lame stuffs like message quoting, annoying ppl, giving random opinions, and some Grand Blue & Temple content-related commands.\nUse bb!help for more info!", inline=False)
    embed.insert_field_at(4, name="Acknowledgements", value = "My sincerest gratitude for my friends Ymity, Anders Hass, Tintin, FIRE2GO, Shibito & Vik for helping me test as well as giving suggestions.\nMy thanks to Gyro, Alan and Norminee for providing me some quality images too.\nAnd last but not least, thank you dear users for using me!!!", inline=False)

    embed.set_thumbnail(url=creator.avatar_url)
    embed.set_footer(text="Made with passion during the summer of 2021. Ah, how much I hate COVID.")
    await ctx.send(embed=embed)

async def reset(ctx):
    guild = ctx.guild
    db.child("guilds").child(guild.id).remove()
    guild_setup(guild)
    await ctx.send("Successfully reset all data of this server. The list of pingable roles are empty now.")

async def roleping_add(ctx, role_id):
    guild = ctx.guild
    if guild is None:
        await ctx.send(f'An error occurred and this server is no longer in my database. Please contact the creator <@{AUTHOR_ID}> for help regarding this matter.')
        return

    if role_id is None:
        await ctx.send("Sorry pal, please specify a role ID for me to configure!")
        return

    role_id = int(role_id)
    searched_role = guild.get_role(role_id)
    if searched_role is None:
        await ctx.send("Sorry pal, you specified an invalid role ID :(")
        return

    db.child("guilds").child(guild.id).child("pingable_roles").update({searched_role.name: "True"})
    await ctx.send(f'Successfully add the role {searched_role.name} to the list of pingable roles!')

async def roleping_remove(ctx, role_id):
    guild = ctx.guild
    if guild is None:
        await ctx.send(f'An error occurred and this server is no longer in my database. Please contact the creator <@{AUTHOR_ID}> for help regarding this matter.')
        return

    if role_id is None:
        await ctx.send("Sorry pal, please specify a role ID for me to configure!")
        return

    role_id = int(role_id)
    searched_role = guild.get_role(role_id)
    if searched_role is None:
        await ctx.send("Sorry pal, you specified an invalid role ID :(")
        return

    db.child("guilds").child(guild.id).child("pingable_roles").child(searched_role.name).remove()
    await ctx.send(f'Successfully remove the role {searched_role.name} from the list of pingable roles!')
async def roleping_list(ctx):
    guild = ctx.guild
    if guild is None:
        await ctx.send(f'An error occurred and this server is no longer in my database. Please contact the creator <@{AUTHOR_ID}> for help regarding this matter.')
        return

    pingable_roles = db.child("guilds").child(guild.id).child("pingable_roles").get().val()
    await ctx.send(f'The list of pingable roles are:\n{", ".join(pingable_roles.keys())}')

@bot.command(aliases=['e'], help="Aliases: e. An user with admin permission edit the configurations of the server. Possible actions are: \nbb!edit reset: Delete all the pingable roles.\nbb!edit roleping/rp add [role_id]: Add a role to the list of pingable roles.\nbb!edit roleping/rp remove/rm [role_id]: Remove a role from the list of pingable roles.\n")
@has_permissions(administrator=True)
async def edit(ctx, category=None, action=None, param=None):
    if category is None:
        await ctx.send("Please specify a config category. For example `bb!edit reset`, etc.")
    elif category == 'reset':
        await reset(ctx)
    elif category == "roleping" or category == "rp":
        if action is None:
            await ctx.send("Please specify an action for the `roleping` category. For example `bb!config roleping add`, `bb!config roleping list`, etc.")
        elif action == 'add':
            await roleping_add(ctx, param)
        elif action == 'remove' or action == 'rm':
            await roleping_remove(ctx, param)
        elif action == "list":
            await roleping_list(ctx)
        else:
            await ctx.send("Sorry my friends, currently the only possible actions for `config roleping` are `add`, `remove/rm` or `list`.")
    elif category == "wiki":
        if action is None:
            await ctx.send("Please specify the name of the wiki command. For example, gb for Grand Blue, etc.")
        elif param is None:
            await ctx.send("Please specify the base wiki link. For example https://grand-blue.fandom.com/wiki")
        else:
            guild = ctx.guild
            db.child("guilds").child(guild.id).child("wiki").update({action: param})
            await ctx.send(f'Successfully add the link {param} for the wiki command `bb!wiki {action}`')
    else:
        await ctx.send("Sorry my friends, currently the only possible categories for config are `roleping/rp` or `reset`.")

@bot.command(name='list', help="List the list of rolepings, or something else.\nbb!list rp/roleping is to list all the pingable roles!")
async def list(ctx, category=None):
    if category is None:
        await ctx.send("Please specify a category to list. For example `bb!list roleping/rp`, etc.")
    elif category == "roleping" or category == "rp":
        await roleping_list(ctx)
    else:
        await ctx.send("Sorry my friends, currently the only possible categories for list are `bb!list roleping/rp`, etc.")

@bot.command(aliases=['w', 'wk'], help="Aliases: w, wk. Post the wiki link of a character")
async def wiki(ctx, manga=None, query=None):
    if manga is None:
        await ctx.send("Please specify the name of the manga.")
        return
    elif query is None:
        await ctx.send("Please specify the name of the query. For example: chisa")
        return
    else:
        guild = ctx.guild
        links = db.child("guilds").child(guild.id).child("wiki").get().val()
        if not manga in links:
            await ctx.send("Please specify a valid name for the manga.")
            return
        base_url = links[manga] + "/Special:Search?query=" + query
        print(base_url)

        page = requests.get(base_url)
        soup = BeautifulSoup(page.content, "html.parser")
        search_elements = soup.find(id="mw-content-text").find_all("li", class_="unified-search__result")
        if len(search_elements) == 0:
            await ctx.send("No available results that match your query.")
        else:
            await ctx.send(search_elements[0].find("a").get("href"))
        return


@bot.command(aliases=['sp'], help="Aliases: sp. Spoiler mark an image. bb!spoiler [message] to send a message, then spoiler mark the old image")
async def spoiler(ctx):
    message = ctx.message
    if len(message.attachments) == 0:
        await ctx.send("Sorry, you did not attach an image in order for me to mark it as spoiler.")
        return
    await message.delete()
    if len(message.content) > 11:
        await ctx.send(ctx.message.content[11:])
    
    image = message.attachments[0]

    out_file = await image.to_file(spoiler=True)
    await ctx.send(file=out_file)

@bot.event
async def on_guild_join(guild):
    # general = find(lambda x: x.name == 'general',  guild.text_channels)
    # if general and general.permissions_for(guild.me).send_messages:
    #     await general.send('Hello {}!'.format(guild.name))
    # print(guild.id)
    # db.child("guilds").child(guild.id)
    guild_setup(guild)

def guild_setup(guild):
    guild_obj = db.child("guilds").child(guild.id)
    guild_obj.set({"name": guild.name})

    #setup wiki
    db.child("guilds").child(guild.id).child("wiki").update({"gb": "https://grand-blue.fandom.com/wiki"})
    db.child("guilds").child(guild.id).child("wiki").update({"grandblue": "https://grand-blue.fandom.com/wiki"})
    db.child("guilds").child(guild.id).child("wiki").update({"temple": "https://tenpuru-no-one-can-live-on-loneliness.fandom.com/wiki"})
    db.child("guilds").child(guild.id).child("wiki").update({"tenpuru": "https://tenpuru-no-one-can-live-on-loneliness.fandom.com/wiki"})
@bot.event
async def on_command_error(ctx, error):
    print(type(error))
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('Sorry my friends, you do not have the necessary permission to make me do this.')
    elif isinstance(error, commands.errors.ChannelNotFound):
        await ctx.send('Channel name is wrong, or you do not need the permission to read messages in this channel :(')
    elif isinstance(error, commands.errors.CommandInvokeError):
        original = error.original
        print(original)
        if isinstance(original, discord.errors.NotFound):
            await ctx.send('No message with such ID exists. Please check it again my friend :<')
    elif isinstance(error, commands.errors.CommandNotFound):
        await ctx.send('My apologies, you specified the wrong command! Type `bb!help` for the list of possible commands.')
bot.run(TOKEN)