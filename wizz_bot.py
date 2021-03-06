from wizz import WizardFactory
import json
from discord.ext import commands
import discord
import logging
import logging.config
import opensea
from random import randrange
from functools import reduce
import random

# Utilities related to Discord
class DiscordUtils:
	@staticmethod
	async def embed(ctx, title, description, thumbnail=None, image=None):
		embed = discord.Embed(title=title, description=description)
		if thumbnail is not None:
			embed.set_thumbnail(url=thumbnail)
		if image is not None:
			embed.set_image(url=image)
		await ctx.send(embed=embed)

	@staticmethod
	async def embed_image(ctx, title, file, filename, description=None, footer=None, url=None):
		embed = discord.Embed(title=title)
		file = discord.File(file, filename=filename)
		embed.set_image(url="attachment://{}".format(filename))
		if description is not None:
			embed.description = description
		if footer is not None:
			embed.set_footer(text=footer)
		if url is not None:
			embed.url = url
		await ctx.send(file=file, embed=embed)

	@staticmethod
	async def embed_fields(ctx, title, fields, inline=True, thumbnail=None, url=None):
		embed = discord.Embed(title=title)
		if thumbnail is not None:
			embed.set_thumbnail(url=thumbnail)
		for field in fields:
			embed.add_field(name=field[0], value=field[1], inline=inline)
		if url is not None:
			embed.url = url
		await ctx.send(embed=embed)


#
# Setup
#
bot = commands.Bot(command_prefix="!")

logging.basicConfig(filename='wizz_bot.log',
                    filemode='a',
                    format='[%(asctime)s] %(name)s - %(message)s',
                    datefmt='%d-%m-%Y @ %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger('wizz_bot')


# 
# Dice
#
@bot.command(name="d20")
async def d20(ctx):
	await dice(ctx, 20)

@bot.command(name="dice", aliases=["d"])
async def dice(ctx, num):
	await DiscordUtils.embed(ctx, "D {}".format(num), "{} rolled {}".format(ctx.message.author, random.randint(1, int(num))))


#
# Lore
#
@bot.command(name="lore")
async def lore(ctx, wiz_id):
	logger.info("LORE %s", wiz_id)
	try:
		wiz_id = int(wiz_id)
		if wiz_id >= 0 and wiz_id < 10000:
			lore = WizardFactory.get_lore(wiz_id)
			await ctx.send(lore)
	except:
		pass

#
# Original artwork
#
@bot.command(name="pic", aliases=["wp", "wizpic"])
async def wizard_profile(ctx, wiz_id):
	logger.info("ARTWORK %s", wiz_id)
	wizard = WizardFactory.get_wizard(wiz_id)
	if wizard is not None:
		await DiscordUtils.embed_image(ctx, wizard.name.title(), wizard.pfp, "{}.png".format(wiz_id))
	else:
		await ctx.send("Could not summon wizard {}".format(wiz_id))

#
# Ho ho ho!
#
@bot.command(name="mount", aliases=["pony"])
async def wizmas(ctx, wiz_id, pony_id=None):
	logger.info("WIZMAS %s %s", wiz_id, pony_id)
	wizard = WizardFactory.get_wizard(wiz_id)
	if wizard is not None:
		if pony_id is None:
			pony_id = randrange(0, 343) # TODO: Remember to update as more are minted
		if wizard.get_pony(pony_id):
			await DiscordUtils.embed_image(ctx, wizard.name.title(), wizard.pony, "{}.png".format(wiz_id))
		else:
			await ctx.send("Could not mount wizard {} to pony {}".format(wiz_id, pony_id))
	else:
		await ctx.send("Could not summon wizard {}".format(wiz_id))


@bot.command(name="ponywalk", aliases=["pw"])
async def pony_walkcycle(ctx, pony_id):
	try:
		img = WizardFactory.get_pony_walkcycle(99999, pony_id)
		await DiscordUtils.embed_image(ctx, "Pony #{}".format(pony_id), img, "ponywalk.gif")
	except:
		await ctx.send("Could not mount {} to {}".format(wiz_id, pony_id))

@bot.command(name="ponyride", aliases=["pr"])
async def pony_walkcycle(ctx, wiz_id, pony_id):
	try:
		wiz_id = int(wiz_id)
		if wiz_id >= 0 and wiz_id <= 9999:
			img = WizardFactory.get_pony_walkcycle(wiz_id, pony_id)
			await DiscordUtils.embed_image(ctx, "Wizard #{} riding Pony #{}".format(wiz_id, pony_id), img, "ponyride.gif")
		else:
			await ctx.send("Wizard {} does not exist".format(wiz_id, pony_id))
	except:
		await ctx.send("Could not mount {} to {}".format(wiz_id, pony_id))

@bot.command(name="sponyride", aliases=["spr"])
async def pony_walkcycle_soul(ctx, wiz_id, pony_id):
	try:
		img = WizardFactory.get_pony_walkcycle(wiz_id, pony_id, is_soul=True)
		await DiscordUtils.embed_image(ctx, "Soul #{} riding Pony #{}".format(wiz_id, pony_id), img, "ponyride.gif")
	except:
		await ctx.send("Could not mount {} to {}".format(wiz_id, pony_id))

# TODO mulitple wizards walk together?

#
# Animated walk cycles
#
async def walkcycle(ctx, wiz_id, large, transparent, familiar=False):
	logger.info("WALKCYCLE %s", wiz_id)
	wizard = WizardFactory.get_wizard(wiz_id)
	if large:
		if familiar:
			file = wizard.walkcycle_familiar_large if not transparent else wizard.walkcycle_familiar_large_nobg
		else:
			file = wizard.walkcycle_large if not transparent else wizard.walkcycle_large_nobg
	else:
		if familiar:
			file = wizard.walkcycle_familiar if not transparent else wizard.walkcycle_familiar_nobg
		else:			
			file = wizard.walkcycle if not transparent else wizard.walkcycle_nobg
	if wizard is not None:
		title = wizard.name.title() if not familiar else "{}'s Familiar".format(wizard.name.title())
		await DiscordUtils.embed_image(ctx, title, file, "{}.gif".format(wiz_id), url=wizard.url)
	else:
		await ctx.send("Could not summon wizard {}".format(wiz_id))


@bot.command(name="walk", aliases=["wc", "gif"])
async def wizard_walkcycle(ctx, wiz_id):
	await walkcycle(ctx, wiz_id, large=True, transparent=False)

@bot.command(name="twalk", aliases=["twc", "tgif"])
async def wizard_walkcycle_large_nobg(ctx, wiz_id):
	await walkcycle(ctx, wiz_id, large=True, transparent=True)

@bot.command(name="walkfam", aliases=["wcf", "giff"])
async def wizard_walkcycle_familiar(ctx, wiz_id):
	await walkcycle(ctx, wiz_id, large=True, transparent=False, familiar=True)

async def walkcycle_familiar(ctx, wiz_id, reversed=False):
	logger.info("WALKCYCLE %s", wiz_id)
	wizard = WizardFactory.get_wizard(wiz_id)
	if wizard is not None:
		if wizard.has_familiar:
			title = "{} with Familiar".format(wizard.name.title())
			await DiscordUtils.embed_image(ctx, title, wizard.walkcycle_with_familiar if not reversed else wizard.walkcycle_with_familiar_reversed, "{}.gif".format(wiz_id), url=wizard.url)
		else:
			await ctx.send("{} does not have a familiar".format(wizard.name.title()))	
	else:
		await ctx.send("Could not summon wizard {}".format(wiz_id))


@bot.command(name="fam", aliases=["bff"])
async def wizard_and_familiar(ctx, wiz_id):
	await walkcycle_familiar(ctx, wiz_id)

@bot.command(name="famr", aliases=["bffr"])
async def wizard_and_familiar_reversed(ctx, wiz_id):
	await walkcycle_familiar(ctx, wiz_id, reversed=True)

#
# Mugshot
#
@bot.command(name="mugshot", aliases=["mug"])
async def wizard_mugshot(ctx, wiz_id):
	logger.info("MUGSHOT %s", wiz_id)
	wizard = WizardFactory.get_wizard(wiz_id)
	if wizard is not None:
		await DiscordUtils.embed_image(ctx, wizard.name.title(), wizard.mugshot, "{}.png".format(wiz_id), url=wizard.url)
	else:
		await ctx.send("Could not summon wizard {}".format(wiz_id))


#
# GM
#
@bot.command(name="gm")
async def wizard_gm(ctx, wiz_id):
	logger.info("GM %s", wiz_id)
	wizard = WizardFactory.get_wizard(wiz_id)
	if wizard is not None:
		await DiscordUtils.embed_image(ctx, wizard.name.title(), wizard.gm, "{}.png".format(wiz_id), url=wizard.url)
	else:
		await ctx.send("Could not summon wizard {}".format(wiz_id))

#
# GM
#
@bot.command(name="say")
async def wizard_gm(ctx, *, msg):
	try:
		words = msg.split()
		has_token_id = words[0].isnumeric()
		wiz_id = words[0] if has_token_id else random.randint(0, 9999)
		logger.info("SAY %s", wiz_id)
		phrase = " ".join(words[1 if has_token_id else 0:])
		wizard, img = WizardFactory.catchphrase(wiz_id, phrase)
		await DiscordUtils.embed_image(ctx, wizard.name.title(), img, "{}.png".format(wiz_id), url=wizard.url)
	except:
		await ctx.send("Could not summon wizard {}".format(wiz_id))


#
# RIP
#
@bot.command(name="rip")
async def wizard_rip(ctx, wiz_id):
	logger.info("RIP %s", wiz_id)
	wizard = WizardFactory.get_wizard(wiz_id)
	if wizard is not None:
		await DiscordUtils.embed_image(ctx, wizard.name.title(), wizard.rip, "{}.png".format(wiz_id), url=wizard.url)
	else:
		await ctx.send("Could not summon wizard {}".format(wiz_id))

#
# Sacred Flame
#
@bot.command(name="flame")
async def flame(ctx):
	logger.info("FLAME")
	filename = "sacred_flame.gif"
	file = "./resources/veil/{}".format(filename)
	title = "Sacred Flame"
	description = """On All Hallows Eve, 2021 the Great Burning began at The Secret Tower.
	
A Wizard and a Flame may be burned to receive a Forgotten Soul.

Burning a Wizard, however, is Dark Magic which is always risky and unpredictable. If you choose to burn a Wizard, there's a chance you may receive something undesirable.

So choose wisely.

[Read more about The Great Burning](https://www.forgottenrunes.com/posts/forgotten-souls)"""
	await DiscordUtils.embed_image(ctx, title, file, filename, description=description)


#
# Run bot
#
try:
	file = open('creds.json', 'r')
	access_token = json.load(file)['access_token']	
	bot.run(access_token)
except:
	print("Missing or faulty creds.json")
