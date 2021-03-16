import os
from configparser import ConfigParser

import typing
from discord.ext import commands
from dotenv import load_dotenv

from manager import NPCGenerator, create_name
from constant_strings import *

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
async def generate(ctx, *tag: typing.Optional[str]):
    traits = npc_generator.generate(*tag)
    if traits['gender'] == WOM:
        e_gender = 'e'
    else:
        e_gender = ""
    if FEM in npc_generator.tags[traits['accessories'].upper()]:
        det_accessories = "une"
    elif MASC in npc_generator.tags[traits['accessories'].upper()]:
        det_accessories = "un"
    elif PLUR in npc_generator.tags[traits['accessories'].upper()]:
        det_accessories = "de"
    elif PLURS in npc_generator.tags[traits['accessories'].upper()]:
        det_accessories = "des"
    else:
        det_accessories = ""
    npc_description = f"{traits['name']} est un{e_gender} {traits['job']} {traits['specie']} plutôt " \
                      f"{traits['appearance']}, {traits['behavior']}, semble être {traits['personality']} et " \
                      f"a {det_accessories} {traits['accessories']}"
    await ctx.send(npc_description)


@bot.command(name="name", help="Generate a name.", aliases=["n"])
async def get_name(ctx, length: typing.Optional[int]):
    if length is None:
        length = 2
    name = create_name(length)
    await ctx.send(name)


bot.run(TOKEN)
