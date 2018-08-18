import discord
from discord.ext import commands

class NoCharacter(commands.CheckFailure):
	pass

def has_char():
	async def predicate(ctx):
		async with ctx.bot.pool.acquire() as conn:
			test = await conn.fetchrow('SELECT * FROM profile WHERE "user"=$1;', ctx.author.id)
		if test:
			return True
		raise NoCharacter()
	return commands.check(predicate)

def has_adventure():
	async def predicate(ctx):
		async with ctx.bot.pool.acquire() as conn:
			return await conn.fetchrow('SELECT * FROM mission WHERE "name"=$1;', ctx.author.id)
	return commands.check(predicate)

def has_no_adventure():
	async def predicate(ctx):
		async with ctx.bot.pool.acquire() as conn:
			return not await conn.fetchrow('SELECT * FROM mission WHERE "name"=$1;', ctx.author.id)
	return commands.check(predicate)

async def user_has_char(bot, userid):
	async with bot.pool.acquire() as conn:
		return await conn.fetchrow('SELECT * FROM profile WHERE "user"=$1;', userid)

async def has_money(bot, userid, money):
	async with bot.pool.acquire() as conn:
		return await conn.fetchval('SELECT money FROM profile WHERE "user"=$1 AND "money">=$2;', userid, money)

def is_admin():
	async def predicate(ctx):
		return ctx.author.id in ctx.bot.config.admins
	return commands.check(predicate)

def is_patron():
	def predicate(ctx):
		member = ctx.bot.get_guild(ctx.bot.config.support_server_id).get_member(ctx.author.id)  # cross server stuff
		if not member:
			return False
		return discord.utils.get(member.roles, name='Donators') is not None or discord.utils.get(member.roles, name='Administrators') is not None
	return commands.check(predicate)

def user_is_patron(bot, userid):
	member = bot.get_guild(bot.config.support_server_id).get_member(userid)  # cross server stuff
	if not member:
		return False
	return discord.utils.get(member.roles, name='Donators') is not None or discord.utils.get(member.roles, name='Administrators') is not None

def is_hypesquad(ctx):
	member = ctx.bot.get_guild(ctx.bot.config.support_server_id).get_member(ctx.author.id)  # cross server stuff
	if not member:
		return False
	return discord.utils.get(member.roles, name='Hypesquad') is not None or discord.utils.get(member.roles, name='Administrators') is not None
