from wizz import WizardFactory
import json
from discord.ext import commands
import discord
import logging
import logging.config
import opensea
from random import randrange
from functools import reduce
import magic

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
# Magic
#
@bot.command(name="magic")
async def do_magic(ctx):
	magic.grant_magic(ctx.message.author.id, 1, ctx.guild.id)


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

#
# Animated walk cycles
#
async def walkcycle(ctx, wiz_id, large, transparent):
	logger.info("WALKCYCLE %s", wiz_id)
	wizard = WizardFactory.get_wizard(wiz_id)
	if large:
		file = wizard.walkcycle_large if not transparent else wizard.walkcycle_large_nobg
	else:
		file = wizard.walkcycle if not transparent else wizard.walkcycle_nobg
	if wizard is not None:
		await DiscordUtils.embed_image(ctx, wizard.name.title(), file, "{}.gif".format(wiz_id), url=wizard.url)
	else:
		await ctx.send("Could not summon wizard {}".format(wiz_id))

@bot.command(name="walk", aliases=["wc", "gif"])
async def wizard_walkcycle(ctx, wiz_id):
	await walkcycle(ctx, wiz_id, False, False)

@bot.command(name="walkbig", aliases=["wcb", "gifbig"])
async def wizard_walkcycle_large(ctx, wiz_id):
	await walkcycle(ctx, wiz_id, True, False)

@bot.command(name="twalk", aliases=["twc", "tgif"])
async def wizard_walkcycle_nobg(ctx, wiz_id):
	await walkcycle(ctx, wiz_id, False, True)

@bot.command(name="twalkbig", aliases=["twcb", "tgifbig"])
async def wizard_walkcycle_large_nobg(ctx, wiz_id):
	await walkcycle(ctx, wiz_id, True, True)

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
