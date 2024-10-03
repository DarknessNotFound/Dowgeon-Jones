# AdminTest.py
import discord
import Logging as Log
import DbManagement as DB
import discord.guild
from discord.ext import tasks, commands
from discord import Guild
import itemGenerator as iGen
from calendarHelper import SECONDS_PER_IN_GAME_DAY

import time
import json

FILE_NAME = "CalendarCommands"
DATE_CHANNEL_ID_FILE = "./databases/shop_channel_data.json"

class ShopManagement(commands.Cog):
    def __init__(self, client):
        self.update_shop.start()
        self.client = client
        self.shops_msg_ids = []

    def cog_unload(self):
        self.update_shop.cancel()
    
    # Commands
    @commands.command(name='shopMelee', help='Generates a random melee weapon.')
    async def randomMeleeWeapon(self, ctx, *args):
        """Generates a random melee weapon.

        Args:
            ctx (_type_): _description_
        """
        try:
            num_weapons = 1
            if len(args) > 0:
                if args[0].isdigit() and int(args[0]) >= 0:
                    num_weapons = int(args[0])

            for i in range(num_weapons):
                await ctx.send(f"{iGen.GenerateMeleeWeapon()}")
            
        except Exception as ex:
            Log.Error(FILE_NAME, "randomMeleeWeapon", str(ex))
            print(f"ERROR: In file \"{FILE_NAME}\" of command \"randomMeleeWeapon\"")
            print(f"Message: {str(ex)}")
            await ctx.send("Error generating a melee weapon, please try again.") 

    @commands.command(name='startShop', help='Starts the random shop generator.')
    async def startShop(self, ctx, *args):
        try:
            num_shops = 1
            if len(args) > 0:
                if args[0].isdigit() and int(args[0]) >= 0:
                    num_shops = int(args[0])

            for i in range(num_shops):
                message = await ctx.send("Starting shop here...")
                self.shops_msg_ids.append((message.channel.id, message.id))
                await message.edit(content=iGen.GenerateMeleeWeapon())
        except Exception as ex:
            Log.Error(FILE_NAME, "startShop", str(ex))
            print(f"ERROR: In file \"{FILE_NAME}\" of command \"startShop\"")
            print(f"Message: {str(ex)}")
            await ctx.send("Error starting the shop, please try again.") 

    @commands.command(name='stopAllShops')
    async def stop_all_shops(self, ctx, *args):
        try:
            self.shops_msg_ids = []
            await ctx.send("Stopped All Shops")
        except Exception as ex:
            Log.Error(FILE_NAME, "stopAllShops", str(ex))
            print(f"ERROR: In file \"{FILE_NAME}\" of command \"stopAllShops\"")
            print(f"Message: {str(ex)}")
            await ctx.send("Error stopping all shops, please try again.") 

    @commands.command(name='refreshAllShops')
    async def stop_all_shops(self, ctx, *args):
        try:
            for msg_id in self.shops_msg_ids:
                channel = await self.client.fetch_channel(msg_id[0])
                message = await channel.fetch_message(msg_id[1])
                new_weapon = iGen.GenerateMeleeWeapon()
                await message.edit(content=new_weapon)
            await ctx.send("Refreshed all shops.")
        except Exception as ex:
            Log.Error(FILE_NAME, "stopAllShops", str(ex))
            print(f"ERROR: In file \"{FILE_NAME}\" of command \"stopAllShops\"")
            print(f"Message: {str(ex)}")
            await ctx.send("Error stopping all shops, please try again.") 

    @tasks.loop(seconds=20.0)
    async def update_shop(self):
        await self.client.wait_until_ready()
        try:
            if time.time() % SECONDS_PER_IN_GAME_DAY >= 21:
                return
            for msg_id in self.shops_msg_ids:
                channel = await self.client.fetch_channel(msg_id[0])
                message = await channel.fetch_message(msg_id[1])
                new_weapon = iGen.GenerateMeleeWeapon()
                await message.edit(content=new_weapon)
        except Exception as ex:
            print(f"ERROR in update_shop: {ex}")

async def setup(client):
    await client.add_cog(ShopManagement(client))
