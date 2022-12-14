from wizz import WizardFactory
import json
from discord.ext import commands
import discord
import logging
import logging.config
from random import randrange
from functools import reduce
import random
from forge import WeaponForge
import asyncio


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
	async def embed_image(ctx, title, file, filename, description=None, footer=None, url=None, fields=None, color=None, thumbnail=None):
		embed = discord.Embed(title=title, color=color)
		file = discord.File(file, filename=filename)
		embed.set_image(url="attachment://{}".format(filename))
		if description is not None:
			embed.description = description
		if footer is not None:
			embed.set_footer(text=footer)
		if url is not None:
			embed.url = url
		if fields is not None:
			for field in fields:
				embed.add_field(name=field[0], value=field[1], inline=False)
		if thumbnail is not None:
			embed.set_thumbnail(url=thumbnail)
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
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

logging.basicConfig(filename='wizz_bot.log',
                    filemode='a',
                    format='[%(asctime)s] %(levelname)s\t%(name)s - %(message)s',
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


#
# Animated walk cycles
#
async def walkcycle(ctx, wiz_id, large, transparent, familiar=False, is_soul=False, is_warrior=False):
	logger.info("WALKCYCLE %s", wiz_id)
	wizard = WizardFactory.get_wizard(wiz_id, is_soul=is_soul, is_warrior=is_warrior)
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

@bot.command(name="wwalk", aliases=["wwc", "wgif"])
async def warrior_walkcycle(ctx, wiz_id):
	await walkcycle(ctx, wiz_id, large=True, transparent=False, is_warrior=True)

@bot.command(name="twwalk", aliases=["twwc", "twgif"])
async def warrior_walkcycle_large_nobg(ctx, wiz_id):
	await walkcycle(ctx, wiz_id, large=True, transparent=True, is_warrior=True)

@bot.command(name="swalk", aliases=["swc", "sgif"])
async def soul_walkcycle(ctx, wiz_id):
	await walkcycle(ctx, wiz_id, large=True, transparent=False, is_soul=True)

@bot.command(name="tswalk", aliases=["tswc", "tsgif"])
async def soul_walkcycle_large_nobg(ctx, wiz_id):
	await walkcycle(ctx, wiz_id, large=True, transparent=True, is_soul=True)


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

@bot.command(name="sgm")
async def wizard_gm(ctx, wiz_id):
	logger.info("GM %s", wiz_id)
	wizard = WizardFactory.get_wizard(wiz_id, is_soul=True)
	if wizard is not None:
		await DiscordUtils.embed_image(ctx, wizard.name.title(), wizard.gm, "{}.png".format(wiz_id), url=wizard.url)
	else:
		await ctx.send("Could not summon soul {}".format(wiz_id))

@bot.command(name="wgm")
async def wizard_gm(ctx, token_id):
	logger.info("GM %s", token_id)
	warrior = WizardFactory.get_wizard(token_id, is_warrior=True)
	if warrior is not None:
		await DiscordUtils.embed_image(ctx, warrior.name.title(), warrior.gm, "{}.png".format(token_id), url=warrior.url)
	else:
		await ctx.send("Could not summon warrior {}".format(token_id))

#
# SAY
#
@bot.command(name="say")
async def wizard_say(ctx, *, msg):
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

@bot.command(name="ssay")
async def soul_say(ctx, *, msg):
	try:
		words = msg.split()
		has_token_id = words[0].isnumeric()
		wiz_id = words[0] if has_token_id else random.choice(WizardFactory.soul_ids)
		logger.info("SAY %s", wiz_id)
		phrase = " ".join(words[1 if has_token_id else 0:])
		wizard, img = WizardFactory.catchphrase(wiz_id, phrase, is_soul=True)
		await DiscordUtils.embed_image(ctx, wizard.name.title(), img, "{}.png".format(wiz_id), url=wizard.url)
	except:
		await ctx.send("Could not summon soul {}".format(wiz_id))

@bot.command(name="wsay")
async def warrior_say(ctx, *, msg):
	try:
		words = msg.split()
		has_token_id = words[0].isnumeric()
		token_id = words[0] if has_token_id else random.randint(0, 16000)
		logger.info("SAY %s", token_id)
		phrase = " ".join(words[1 if has_token_id else 0:])
		warrior, img = WizardFactory.catchphrase(token_id, phrase, is_warrior=True)
		await DiscordUtils.embed_image(ctx, warrior.name.title(), img, "{}.png".format(token_id), url=warrior.url)
	except:
		await ctx.send("Could not summon warrior {}".format(token_id))


#
# POSTER
#
@bot.command(name="poster")
async def wizard_poster(ctx, wiz_id):
	try:
		logger.info("POSTER %s", wiz_id)
		wizard, img = WizardFactory.anatomy(wiz_id)
		await DiscordUtils.embed_image(ctx, wizard.name.title(), img, "{}.png".format(wiz_id), url=wizard.url)
	except:
		await ctx.send("Could not summon wizard {}".format(wiz_id))

@bot.command(name="wposter")
async def warrior_poster(ctx, token_id):
	try:
		logger.info("POSTER %s", token_id)
		warrior, img = WizardFactory.anatomy(token_id, is_warrior=True)
		await DiscordUtils.embed_image(ctx, warrior.name.title(), img, "{}.png".format(token_id), url=warrior.url)
	except:
		await ctx.send("Could not summon warrior {}".format(token_id))

@bot.command(name="sposter")
async def soul_poster(ctx, token_id):
	try:
		logger.info("POSTER %s", token_id)
		soul, img = WizardFactory.anatomy(token_id, is_soul=True)
		await DiscordUtils.embed_image(ctx, soul.name.title(), img, "{}.png".format(token_id), url=soul.url)
	except:
		await ctx.send("Could not summon soul {}".format(token_id))

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
# Wrapper for our bot, used by Forge to callback
#
class BotWrapper(object):
	def __init__(self, bot):
		self.bot = bot

	def on_warrior_weapon_forged(self, token_id, lock_id):
		fut = asyncio.run_coroutine_threadsafe(self.__on_warrior_weapon_forged(token_id, lock_id), bot.loop)
		fut.result()

	async def __on_warrior_weapon_forged(self, token_id, item_id):
		logger.info("FORGED %s", token_id)
		try:
			await bot.wait_until_ready()
			warrior_file = WeaponForge.get_warrior(token_id)
			warrior_meta = WeaponForge.get_warrior_meta(token_id)
			warrior_attributes = warrior_meta['attributes']
			warrior_name = warrior_meta['name']
			warrior_weapon = next(filter(lambda a: a['trait_type'] == 'weapon', warrior_attributes))['value']
			warrior_forged_with = next(filter(lambda a: a['trait_type'] == 'forged_with', warrior_attributes))['value']
			forged_with_url = WeaponForge.Router.treat_url(item_id) if warrior_forged_with == "Gold Nugget" else WeaponForge.Router.lock_url(item_id)
			fields = []
			fields.append(("Weapon", warrior_weapon))
			fields.append(("Forged with", warrior_forged_with))
			fields.append(("Warrior", "[{}]({})".format(warrior_name, "https://opensea.io/assets/ethereum/0x9690b63eb85467be5267a3603f770589ab12dc95/{}".format(token_id))))
			# burn-chat: 903730142155788388
			# test-chat: 437876896664125443
			channel = bot.get_channel(437876896664125443)
			await DiscordUtils.embed_image(channel, "A Weapon has been Forged!", warrior_file, warrior_file.split('/')[-1], fields=fields, color=discord.Colour.gold(), thumbnail=forged_with_url)
		except Exception as e:
			logger.error(e)


def main():
	#
	# Observers
	#
	try:
		obvs = WeaponForge.Observer(BotWrapper(bot))
		obvs.start_worker()
	except:
		print("Could not start WeaponForge.Observer")


	#
	# Run bot
	#
	try:
		file = open('creds.json', 'r')
		access_token = json.load(file)['access_token']
		bot.run(access_token)
	except Exception as e:
		print(e)

if __name__ == '__main__':
    main()
