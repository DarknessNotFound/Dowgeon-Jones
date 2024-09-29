# AdminTest.py
import discord
import Logging as Log
from discord.ext import commands
from asyncio import sleep

FILE_NAME = "AdminTest"
class AdminTest(commands.Cog):
    def __init__(self, client):
        self.client = client
    # Commands
    @commands.command(name='echo', help='Echos what user said.')
    async def echo(self, ctx, *args):
        """Echos what was inputed.

        Args:
            ctx (_type_): _description_
        """        
        try:
            Log.Command(ctx.author.id, "Echo", ' '.join(args))
            await ctx.send(' '.join(args))
        except Exception as ex:
            Log.Error(FILE_NAME, "echo", str(ex))

    @commands.command(name='ThrowError', help='Function that throws an error, mostly for logging sake')
    async def ThrowError(self, ctx, *args):
        try:
            Log.Command(ctx.author.id, "ThrowError", ' '.join(args))
            await ctx.send("Throwing a test error...")
            raise Exception("This is a test error, ignore.")
        except Exception as ex:
            Log.Error(FILE_NAME, "throwError", str(ex))
    
    @commands.command(name='editMessageStart')
    async def EditMessageStart(self, ctx, *args):
        try:
            message = await ctx.send("Testing things")
            print(message)
            print(f"Message Id: {message.id}")
            await sleep(2)
            print("Sleep done.")
            await message.edit(content="This message was edited")
        except Exception as ex:
            Log.Error(FILE_NAME, "throwError", str(ex))

    @commands.command(name='editMessageEdit')
    async def EditMessageEdit(self, ctx, *args):
        try:
            Log.Command(ctx.author.id, "ThrowError", ' '.join(args))
            await ctx.send("Throwing a test error...")
            raise Exception("This is a test error, ignore.")
        except Exception as ex:
            Log.Error(FILE_NAME, "throwError", str(ex))

async def setup(client):
    await client.add_cog(AdminTest(client))
