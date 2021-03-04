import os
from configparser import ConfigParser

import typing
from discord.ext import commands
from dotenv import load_dotenv

from manager import NPCGenerator

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!')

npc = ConfigParser()
npc.read("npc.ini", "utf8")
npc_generator = NPCGenerator(npc)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.command(name="generate", help="Generate a npc.", aliases=["g"])
async def generate(ctx, tag: typing.Optional[str]):
    response = npc_generator.generate(tag)
    await ctx.send(response)


bot.run(TOKEN)
