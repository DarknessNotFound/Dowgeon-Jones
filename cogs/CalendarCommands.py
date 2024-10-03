# AdminTest.py
import discord
import Logging as Log
import DbManagement as DB
import discord.guild
from discord.ext import tasks, commands
from discord import Guild
from calendarHelper import PrettyPrintDate, MONTH_NAMES, TimeLengthPrettyPrint
import calendarHelper

import time
import json

FILE_NAME = "CalendarCommands"
DATE_CHANNEL_ID_FILE = "./Databases/date_channel_id.json"

class Calendar(commands.Cog):
    def __init__(self, client):
        print(f"Starting In-game Date: {PrettyPrintDate(time.time(), True)}")
        print(f"Starting In-game Date: {PrettyPrintDate(time.time(), False)}")
        self.index = 0
        self.printer.start()
        self.date_display.start()
        self.client = client
        try:
            with open(DATE_CHANNEL_ID_FILE) as f:
                self.voice_chat_d = json.load(f)
        except Exception as ex:
            print(f"ERROR loading Calendar cogs: {ex}")
            self.voice_chat_d = {}
        # print([c.name for c in client.get_all_channels()])
        # self.guild.create_text_channel(self, name="testing-pi")
        #print(f"Channels: {channels}")f

    def cog_unload(self):
        self.printer.cancel()
        self.date_display.cancel()

        for channel_id in self.voice_chat_d.values():
            channel = self.client.get_channel(channel_id)
            channel.delete()
        
        json.dump( self.voice_chat_d, open( DATE_CHANNEL_ID_FILE, 'w' ) )
    # Commands

    @commands.command(name='today', help='Displays the current date.')
    async def today(self, ctx, *args):
        """Displays the current date

        Args:
            ctx (_type_): _description_
        """
        try:
            await ctx.send(f"Today is {PrettyPrintDate(time.time())}")
            
        except Exception as ex:
            Log.Error(FILE_NAME, "today", str(ex))
            print(f"ERROR: In file \"{FILE_NAME}\" of command \"today\"")
            print(f"Message: {str(ex)}")
            await ctx.send("Error calculating today, please try again.") 

    @commands.command(name='date', help='Displays the current date. [epoch] adding an interger of epoch time will convert any epoch time.')
    async def date(self, ctx, *args):
        """Displays the date, defaults current date.

        Args:
            ctx (_type_): _description_
        """
        try:
            if len(args) > 0:
                if args[0].isdigit() and int(args[0]) >= 0:
                    await ctx.send(f"Datetime: {PrettyPrintDate(int(args[0]), True)}")
                else:
                    await ctx.send(f"ERROR: please input a positive integer")
            else:
                await ctx.send(f"Datetime: {PrettyPrintDate(time.time(), True)}")
            
        except Exception as ex:
            Log.Error(FILE_NAME, "date", str(ex))
            print(f"ERROR: In file \"{FILE_NAME}\" of command \"date\"")
            print(f"Message: {str(ex)}")
            await ctx.send("Error calculating time, please try again.")

    @commands.command(name='time', help='Displays the current time. [epoch] adding an interger of epoch time will convert any epoch time.')
    async def time(self, ctx, *args):
        """Displays the date, defaults current date.

        Args:
            ctx (_type_): _description_
        """
        try:
            if len(args) > 0:
                if args[0].isdigit() and int(args[0]) >= 0:
                    await ctx.send(f"Datetime: {PrettyPrintDate(int(args[0]), False)}")
                else:
                    await ctx.send(f"ERROR: please input a positive integer")
            else:
                await ctx.send(f"Datetime: {PrettyPrintDate(time.time(), False)}")
            
        except Exception as ex:
            Log.Error(FILE_NAME, "time", str(ex))
            print(f"ERROR: In file \"{FILE_NAME}\" of command \"time\"")
            print(f"Message: {str(ex)}")
            await ctx.send("Error calculating time, please try again.")

    @commands.command(name='timeTilNextDay', help='Displays the number of epoch minutes until the start of the next day')
    async def timeTilNextDay(self, ctx, *args):
        """Displays the number of epoch minutes until the start of the next day

        Args:
            ctx (_type_): _description_
        """
        def timeTil(epoch: float) -> float:
            return calendarHelper.SECONDS_PER_IN_GAME_DAY - epoch % calendarHelper.SECONDS_PER_IN_GAME_DAY
        
        try:
            if len(args) > 0:
                if args[0].isdigit() and int(args[0]) >= 0:
                    await ctx.send(f"Time until next day is {round(int(timeTil(int(args[0])))/60/60, 2)} hours")
                else:
                    await ctx.send(f"ERROR: please input a positive integer")
            else:
                await ctx.send(f"Time Until: {round(int(timeTil(time.time()))/60/60, 4)} hours")
            
        except Exception as ex:
            Log.Error(FILE_NAME, "time", str(ex))
            print(f"ERROR: In file \"{FILE_NAME}\" of command \"time\"")
            print(f"Message: {str(ex)}")
            await ctx.send("Error calculating time, please try again.")

    @commands.command(name='duration', 
        help='\tduration start end [flags]\nCalculates the time difference in game between two epoch seconds.\n-c: concise display\n-d: days only\n-h: hours only\n-m: minutes only\n-s: seconds only')
    async def duration(self, ctx, *args):
        """Calculates the duration in game.

        Args:
            ctx (_type_): _description_
        """
        try:

            if len(args) < 2:
                await ctx.send(f"ERROR: please input at least two positive integers.")
                return
            
            start = args[0]
            end = args[1]
            flag = ""
            if len(args) >= 3:
                flag = args[2]

            if not start.isdigit():
                await ctx.send(f"ERROR: start must be a integer.")
                return
            
            if not end.isdigit():
                await ctx.send(f"ERROR: end must be a integer.")
                return
            
            start = int(start)
            end = int(end)
            if start < 0:
                await ctx.send(f"WARNING: start must be non-negative, setting start to 0.")
                start = 0

            if end < 0:
                await ctx.send(f"WARNING: end must be non-negative, setting end to be one higher than the start.")
                end = start + 1

            if flag == "":
                await ctx.send(f"{TimeLengthPrettyPrint(start, end)}")
            elif flag == "-c":
                await ctx.send(f"{TimeLengthPrettyPrint(start, end, True)}")
            elif flag == "-d":
                await ctx.send(f"{calendarHelper.TimeLengthDays(start, end):.2f} days")
            elif flag == "-h":
                await ctx.send(f"{calendarHelper.TimeLengthHours(start, end):.2f} hours")
            elif flag == "-m":
                await ctx.send(f"{calendarHelper.TimeLengthMinutes(start, end):.2f} minutes")
            elif flag == "-s":
                await ctx.send(f"{calendarHelper.TimeLengthSeconds(start, end):.2f} seconds")
            else:
                await ctx.send(f"WARNING: didn't understand flag. Flags are: \n\t-c: concise display\n\t-d: days only\n\t-h: hours only\n\t-m: minutes only\n\t-s: seconds only")
                await ctx.send(f"{TimeLengthPrettyPrint(start, end)}")

            
        except Exception as ex:
            Log.Error(FILE_NAME, "time", str(ex))
            print(f"ERROR: In file \"{FILE_NAME}\" of command \"time\"")
            print(f"Message: {str(ex)}")
            await ctx.send("Error calculating time, please try again.") 

    @commands.command(name='months', help='Displays the months of the year.')
    async def months(self, ctx, *args):
        """Displays the current date

        Args:
            ctx (_type_): 
        """
        try:
            msg = ""
            for month in MONTH_NAMES.values():
                msg += month + "\n"

            await ctx.send(msg)
            
        except Exception as ex:
            Log.Error(FILE_NAME, "months", str(ex))
            print(f"ERROR: In file \"{FILE_NAME}\" of command \"months\"")
            print(f"Message: {str(ex)}")
            await ctx.send("Error calculating months, please try again.") 

    @tasks.loop(seconds=10.0)
    async def printer(self):
        await self.client.wait_until_ready()
        # print(self.index)
        self.index += 1
    
    @tasks.loop(seconds=5*61.0)
    async def date_display(self):
        await self.client.wait_until_ready()
        for guild in self.client.guilds:
            if str(guild.id) not in self.voice_chat_d:
                channel = await guild.create_voice_channel(name = f"{PrettyPrintDate(time.time(), True)}")
                self.voice_chat_d[str(guild.id)] = channel.id
            else:
                channel = self.client.get_channel(self.voice_chat_d[str(guild.id)])
                if channel is None:
                    channel = await guild.create_voice_channel(name = f"{PrettyPrintDate(time.time(), True)}")
                    self.voice_chat_d[str(guild.id)] = channel.id
                else:
                    await channel.edit(name=PrettyPrintDate(time.time(), True))
        json.dump( self.voice_chat_d, open( DATE_CHANNEL_ID_FILE, 'w' ) )

async def setup(client):
    await client.add_cog(Calendar(client))
