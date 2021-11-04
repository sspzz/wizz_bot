from wizz import WizardFactory
import json
from discord.ext import commands
import discord
import logging
import logging.config
import opensea
from functools import reduce

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
# Animated turnaround
#
async def turnaround(ctx, wiz_id, large, transparent):
	logger.info("TURNAROUND %s", wiz_id)
	wizard = WizardFactory.get_wizard(wiz_id)
	if large:
		file = wizard.turnaround_large if not transparent else wizard.turnaround_large_nobg
	else:
		file = wizard.turnaround if not transparent else wizard.turnaround_nobg
	if wizard is not None:
		await DiscordUtils.embed_image(ctx, wizard.name.title(), file, "{}.gif".format(wiz_id), url=wizard.url)
	else:
		await ctx.send("Could not summon wizard {}".format(wiz_id))

@bot.command(name="gif", aliases=["wg", "wizgif"])
async def wizard_turnaround(ctx, wiz_id):
	await turnaround(ctx, wiz_id, False, False)

@bot.command(name="gifbig", aliases=["wgb", "wizgifbig"])
async def wizard_turnaround_large(ctx, wiz_id):
	await turnaround(ctx, wiz_id, True, False)

@bot.command(name="tgif", aliases=["twg", "twizgif"])
async def wizard_turnaround_nobg(ctx, wiz_id):
	await turnaround(ctx, wiz_id, False, True)

@bot.command(name="tgifbig", aliases=["twgb", "twizgifbig"])
async def wizard_turnaround_large_nobg(ctx, wiz_id):
	await turnaround(ctx, wiz_id, True, True)

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
# Animated mugshot
#
@bot.command(name="gifmug", aliases=["mugturn", "mgif"])
async def wizard_mugshot_turnaround(ctx, wiz_id):
	logger.info("MUGSHOT TURNAROUND %s", wiz_id)
	wizard = WizardFactory.get_wizard(wiz_id)
	if wizard is not None:
		await DiscordUtils.embed_image(ctx, wizard.name.title(), wizard.turnaround_mugshot, "{}.gif".format(wiz_id), url=wizard.url)
	else:
		await ctx.send("Could not summon wizard {}".format(wiz_id))

@bot.command(name="gifmugbig", aliases=["mugturnbig", "mgifbig"])
async def wizard_mugshot_turnaround_large(ctx, wiz_id):
	logger.info("MUGSHOT TURNAROUND %s", wiz_id)
	wizard = WizardFactory.get_wizard(wiz_id)
	if wizard is not None:
		await DiscordUtils.embed_image(ctx, wizard.name.title(), wizard.turnaround_mugshot_large, "{}.gif".format(wiz_id), url=wizard.url)
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
# Listings & Sales
#
@bot.command(name="listings", aliases=["l", "list"])
async def listings(ctx, num):
	logger.info("LISTINGS %s", num)
	try:
		num = int(num)
		listings = opensea.get_listings(opensea.contract_wizards, min(20, num))
		thumbnail = listings[0].image_url
		fields = map(lambda l: (l.name, "[#{}]({}) listed for {} {}".format(l.token_id, l.url, l.price, l.currency)), listings)
		await DiscordUtils.embed_fields(ctx, "Recent Listings", fields=fields, thumbnail=thumbnail, inline=False)
	except Exception as e:
		print("Error: {}".format(str(e)))

@bot.command(name="soulistings", aliases=["sl", "slist"])
async def listings(ctx, num):
	logger.info("LISTINGS %s", num)
	try:
		num = int(num)
		listings = opensea.get_listings(opensea.contract_souls, min(20, num))
		thumbnail = listings[0].image_url
		fields = map(lambda l: (l.name, "[#{}]({}) listed for {} {}".format(l.token_id, l.url, l.price, l.currency)), listings)
		await DiscordUtils.embed_fields(ctx, "Recent Listings", fields=fields, thumbnail=thumbnail, inline=False)
	except Exception as e:
		print("Error: {}".format(str(e)))

@bot.command(name="sales", aliases=["s"])
async def sales(ctx, num):
	logger.info("SALES %s", num)
	try:
		num = int(num)
		res = opensea.get_sales(opensea.contract_wizards, min(20, num))
		thumbnail = res[0].image_url
		fields = map(lambda l: (l.name, "[#{}]({}) sold for {} {}".format(l.token_id, l.url, l.price, l.currency)), res)
		await DiscordUtils.embed_fields(ctx, "Recent Sales", fields=fields, thumbnail=thumbnail, inline=False)
	except Exception as e:
		print("Error: {}".format(str(e)))

@bot.command(name="soulsales", aliases=["ssales", "ss"])
async def soul_sales(ctx, num):
	logger.info("SSALES %s", num)
	try:
		num = int(num)
		res = opensea.get_sales(opensea.contract_souls, min(20, num))
		thumbnail = res[0].image_url
		fields = map(lambda l: (l.name, "[#{}]({}) sold for {} {}".format(l.token_id, l.url, l.price, l.currency)), res)
		await DiscordUtils.embed_fields(ctx, "Recent Sales", fields=fields, thumbnail=thumbnail, inline=False)
	except Exception as e:
		print("Error: {}".format(str(e)))


#
# Sacred Flame
#
@bot.command(name="flame")
async def flame(ctx):
	logger.info("FLAME")
	listing = opensea.get_latest_sale(opensea.contract_flames)
	filename = "sacred_flame.gif"
	file = "./resources/veil/{}".format(filename)
	title = "Sacred Flame"
	description = """On All Hallows Eve, 2021 the Great Burning began at The Secret Tower.
	
A Wizard and a Flame may be burned to receive a Forgotten Soul.

Burning a Wizard, however, is Dark Magic which is always risky and unpredictable. If you choose to burn a Wizard, there's a chance you may receive something undesirable.

So choose wisely.

[Read more about The Great Burning](https://www.forgottenrunes.com/posts/forgotten-souls)"""
	floor = "Last price: {} {}".format(listing.price, listing.currency)
	await DiscordUtils.embed_image(ctx, title, file, filename, description=description, footer=floor, url=listing.url)


#
# Recurring tasks, like checking sales
#
from discord.ext import tasks
import datetime
import calendar

@tasks.loop(seconds=60)
async def check_soul_sales():
	# sales 863044365299220511
	# live-burn-chat 903730142155788388
	# wiz-bots 896204060405940245
	# wenmoon 437876896664125443
	sales_channels = [437876896664125443, 896204060405940245, 903730142155788388]

	try:
		prev_latest_sale = float(next(open('latest_sale_souls.txt', 'r')))
		res = opensea.get_sales(opensea.contract_souls, 10, after=prev_latest_sale)
		if res is not None:
			for sale in res:
				for channel in sales_channels:
					title = "New Sale: {}".format(sale.name)
					description = sale.date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
					fields = []
					fields.append(("Amount", "{} {}".format(sale.price, sale.currency)))
					if sale.seller is not None:
						fields.append(("Seller", "[{}]({}) ({})".format(sale.seller.wallet[0:8], sale.seller.opensea_profile, sale.seller.name)))
					if sale.buyer is not None:
						fields.append(("Buyer", "[{}]({}) ({})".format(sale.buyer.wallet[0:8], sale.buyer.opensea_profile, sale.buyer.name)))
					await DiscordUtils.embed_fields(bot.get_channel(channel), title, fields=fields, thumbnail=sale.image_url, inline=False, url=sale.permalink)
			new_latest_sale = calendar.timegm(res[0].date.timetuple())+1
	except:
		# First time we run, get the latest sale and store timestamp
		res = opensea.get_sales(opensea.contract_souls, 1)		
		new_latest_sale = calendar.timegm(res[0].date.timetuple())+1

	try:
		out = str(new_latest_sale)
		ts_file = open('latest_sale_souls.txt', 'w')
		ts_file.write(out)
		ts_file.close()
	except:
		pass


@check_soul_sales.before_loop
async def check_soul_sales_before():
    await bot.wait_until_ready()

# No need, RuneBot now supports Soul sales :)
# check_soul_sales.start()


#
# Run bot
#
try:
	file = open('creds.json', 'r')
	access_token = json.load(file)['access_token']	
	bot.run(access_token)
except:
	print("Missing or faulty creds.json")
