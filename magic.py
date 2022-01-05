import json

def __magic_file(guild_id: int) -> str:
	return "magic{}.json".format(guild_id)

def __load_magic(guild_id: int) -> dict:
	try:
		magicf = open(__magic_file(guild_id), 'r')
		return json.load(magicf)
	except:
		print("Creating new magic")
		magic = dict()
		__save_magic(magic, guild_id)
		return magic

def __save_magic(magic: dict, guild_id: int):
	with open(__magic_file(guild_id), 'w') as magicf:
		json.dump(magic, magicf)


class UserMagic(object):
	def __init__(self, user_id, balance, rank):
		self.user_id = user_id
		self.balance = balance
		self.rank = rank

def rankings(guild_id: int) -> list:
	magic = list(map(lambda e: (int(e[0]), e[1]), __load_magic(guild_id).items()))
	return sorted(magic, key=lambda x: x[1], reverse=True)

def user(guild_id: int, user_id: int) -> UserMagic:
	magic = rankings(guild_id)
	entry = [rank for rank in magic if rank[0] == user_id]
	# handle empty?
	return UserMagic(entry[0][0], entry[0][1], magic.index(entry[0])+1)

def grant_magic(user_id: int, points: int, guild_id: int):
	magic = __load_magic(guild_id)
	try:
		magic[str(user_id)] += points
	except KeyError:
		magic[str(user_id)] = points
	magic[str(user_id)] = max(0, magic[str(user_id)])
	__save_magic(magic, guild_id)
