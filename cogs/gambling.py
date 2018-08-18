import discord, random, os
from discord.ext import commands
from discord.ext.commands import BucketType
from utils.checks import *

class Gambling:

	def __init__(self, bot):
		self.bot = bot

	@commands.cooldown(1,5,BucketType.user)
	@commands.command(description="Draw a card!", aliases=["card"])
	async def draw(self, ctx):
		await ctx.trigger_typing()
		files = os.listdir("cards")
		await ctx.send(file=discord.File(f"cards/{random.choice(files)}"))

	@has_char()
	@commands.cooldown(1,5,BucketType.user)
	@commands.command(description="Flip a coin to win some money!", aliases=["coin"])
	async def flip(self, ctx, side:str="heads", amount:int=0):
		side = side.lower()
		if side != "heads" and side != "tails":
			return await ctx.send(f"Use `heads` or `tails` instead of `{side}`.")
		if amount < 0:
			return await ctx.send("Invalid money amount. Must be 0 or higher.")
		if amount > 100000:
			return await ctx.send("You will think of a better way to spend this.")
		if not await has_money(self.bot, ctx.author.id, amount):
			return await ctx.send("You are too poor.")
		result = random.choice(["heads", "tails"])
		if result == "heads":
			resultemoji = "<:heads:437981551196897281>"
		else:
			resultemoji = "<:tails:437981602518138890>"
		async with self.bot.pool.acquire() as conn:
			if result == side:
				await conn.execute('UPDATE profile SET money=money+$1 WHERE "user"=$2;', amount, ctx.author.id)
				await ctx.send(f"{resultemoji} It's **{result}**! You won **${amount}**!")
			else:
				await conn.execute('UPDATE profile SET money=money-$1 WHERE "user"=$2;', amount, ctx.author.id)
				await ctx.send(f"{resultemoji} It's **{result}**! You lost **${amount}**!")

	@has_char()
	@commands.command(description="Roll the dice and win some money!")
	@commands.cooldown(1,5,BucketType.user)
	async def bet(self, ctx, maximum:int=6, tip:int=6, money:int=0):
		if maximum < 2:
			return await ctx.send("Invalid Maximum.")
		if tip > maximum or tip < 1:
			return await ctx.send(f"Invalid Tip. Must be in the Range of `1` to `{maximum}`.")
		if money < 0:
			return await ctx.send("Invalid money amount. Must be 0 or higher.")
		if money > 100000:
			return await ctx.send("Spend it in a better way. C'mon!")
		if not await has_money(self.bot, ctx.author.id, money):
			return await ctx.send("You're too poor.")
		randomn = random.randint(1, maximum)
		async with self.bot.pool.acquire() as conn:
			if randomn == tip:
				await conn.execute('UPDATE profile SET money=money+$1 WHERE "user"=$2;', money*(maximum-1), ctx.author.id)
				await ctx.send(f"You won **${money*(maximum-1)}**! The random number was `{randomn}`, you tipped `{tip}`.")
			else:
				await conn.execute('UPDATE profile SET money=money-$1 WHERE "user"=$2;', money, ctx.author.id)
				await ctx.send(f"You lost **${money}**! The random number was `{randomn}`, you tipped `{tip}`.")



def setup(bot):
	bot.add_cog(Gambling(bot))
