import discord
from discord.ext import commands

from youtube_dl import YoutubeDL

FIVE_MINUTES = 10.0
class music_youtube_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
        #all the music related stuff
        self.is_playing = False

        # array containing song
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio',  'noplaylist':'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        self.vc = ""

     #searching the item on youtube
    def search_yt(self, item):
        if len(item) >= 23 and item[:23] == "https://www.youtube.com":
            with YoutubeDL(self.YDL_OPTIONS) as ydl:
                try: 
                    info = ydl.extract_info(url=item, download=False)
                except Exception: 
                    return False
            return {'source': info['formats'][0]['url'], 'title': info['title']}

        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try: 
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception: 
                return False

        return {'source': info['formats'][0]['url'], 'title': info['title']}

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            #get the first url
            m_url = self.music_queue[0]['source']

            #remove the first element as you are currently playing it
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False
            

    # infinite loop checking 
    # only usable if already in a voice channel
    async def play_music(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0]['source']
            
            #try to connect to voice channel if you are not already connected
            
            print(self.music_queue)
            #remove the first element as you are currently playing it
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    @commands.command(name="join", help="Join a channel to play music there.")
    async def join(self, ctx):
        if self.vc == "" or not self.vc.is_connected() or self.vc == None:
            self.vc = await ctx.author.voice.channel.connect()
        else:
            await ctx.send("I am already connected to a voice channel!")
        
        # while self.vc != "":
        #     start_cd = time.time()
        #     while len(self.music_queue) == 0:
        #         if self.is_playing == True:
        #             break
        #         print(time.time() - start_cd)
        #         if time.time() - start_cd > FIVE_MINUTES:
        #             self.vc.stop()
        #             await ctx.voice_client.disconnect()
        #             return  

    @commands.command(name="play", help="Plays a selected song from youtube")
    async def p(self, ctx, *args):
        if self.vc == "" or not self.vc.is_connected() or self.vc == None:
            await ctx.send("I am not connected to a voice channel! Use `bb!join` to connect me to a voice channel first.")
            return

        query = " ".join(args)
        
        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            #you need to be connected so that the bot knows where to go
            await ctx.send("Connect to a voice channel!")
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("Could not download the song. Incorrect format try another keyword. This could be due to playlist or a livestream format.")
            else:
                self.music_queue.append(song)
                
                if self.is_playing == False:
                    await self.play_music()

    @commands.command(name="queue", help="Displays the current songs in queue")
    async def q(self, ctx):
        retval = ""
        for i in range(0, len(self.music_queue)):
            retval += "{index}".format(index = i+1) + self.music_queue[i]['title'] + "\n"

        print(retval)
        if retval != "":
            await ctx.send(retval)
        else:
            await ctx.send("No songs in queue!")

    @commands.command(name="skip", help="Skips the current song being played")
    async def skip(self, ctx):
        if self.vc == "" or not self.vc.is_connected() or self.vc == None:
            await ctx.send("I am not connected to a voice channel! Use `bb!join` to connect me to a voice channel first.")
        if self.vc != "" and self.vc:
            self.vc.stop()
            #try to play next in the queue if it exists
            await self.play_music()

    @commands.command(name="dc", help="Disconnect the bot from voice channel.")
    async def disconnect(self, ctx):
        self.vc.stop()
        self.music_queue = []
        await ctx.voice_client.disconnect()