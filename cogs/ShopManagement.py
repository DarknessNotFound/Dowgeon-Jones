# AdminTest.py
import discord
import Logging as Log
import DbManagement as DB
import discord.guild
from discord.ext import tasks, commands
from discord import Guild
import itemGenerator as iGen

import time
import json

FILE_NAME = "CalendarCommands"
DATE_CHANNEL_ID_FILE = "./Databases/shop_channel_data.json"

class ShopManagement(commands.Cog):
    def __init__(self, client):
        self.client = client
    
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

async def setup(client):
    await client.add_cog(ShopManagement(client))
