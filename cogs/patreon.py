import discord, functools
from io import BytesIO
from discord.ext import commands
from cogs.rpgtools import makebg
from utils.checks import *
import copy

class Patreon:

	def __init__(self, bot):
		self.bot = bot

	@is_patron()
	@has_char()
	@commands.command(description="[Patreon Only] Changes a weapon name.")
	async def weaponname(self, ctx, itemid: int, *, newname: str):
		if len(newname)>20:
			return await ctx.send("Name too long.")
		async with self.bot.pool.acquire() as conn:
			item = await conn.fetchrow('SELECT * FROM allitems WHERE "owner"=$1 and "id"=$2;', ctx.author.id, itemid)
			if not item:
				return await ctx.send(f"You don't own an item with the ID `{itemid}`.")
			await conn.execute('UPDATE allitems SET "name"=$1 WHERE "id"=$2;', newname, itemid)
		await ctx.send(f"The item with the ID `{itemid}` is now called `{newname}`.")

	@is_patron()
	@has_char()
	@commands.command(name="background", description="[Patreon Only] Changes your profile background.")
	async def _background(self, ctx, url: str=None):
		premade = [f"{self.bot.BASE_URL}/profile/premade1.png", f"{self.bot.BASE_URL}/profile/premade2.png", f"{self.bot.BASE_URL}/profile/premade3.png", f"{self.bot.BASE_URL}/profile/premade4.png"]
		if not url:
			return await ctx.send(f"Please specify either a premade background (`1` to `{len(premade)}`), a custom URL or use `reset` to use the standard image.")
		elif url == "reset":
			url = 0
		elif url.startswith("http") and (url.endswith(".png") or url.endswith(".jpg") or url.endswith(".jpeg")):
			url = url
		else:
			try:
				if int(url) in range(1, len(premade)+1):
					url = premade[int(url)-1]
				else:
					return await ctx.send("That is not a valid premade background.")
			except:
				return await ctx.send("I couldn't read that URL. Does it start with `http://` or `https://` and is either a png or jpeg?")
		async with self.bot.pool.acquire() as conn:
			try:
				await conn.execute('UPDATE profile SET "background"=$1 WHERE "user"=$2;', url, ctx.author.id)
			except:
				return await ctx.send("The URL is too long.")
		if url != 0:
			await ctx.send(f"Your new profile picture is now:\n{url}")
		else:
			await ctx.send("Your profile picture has been resetted.")

	@is_patron()
	@commands.command(description="[Patreon Only] Generates a background image.")
	async def makebackground(self, ctx, url: str, overlaytype: int):
		if overlaytype not in [1,2]:
			return await ctx.send("User either `1` or `2` as the overlay type.")
		if not url.startswith("http") and (url.endswith(".png") or url.endswith(".jpg") or url.endswith(".jpeg")):
			return await ctx.send("I couldn't read that URL. Does it start with `http://` or `https://` and is either a png or jpeg?")
		async with self.bot.session.get(url) as req:
			background = BytesIO(await req.read())
		background.seek(0)
		thing = functools.partial(makebg, background, overlaytype)
		output_buffer = await self.bot.loop.run_in_executor(None, thing)
		f = copy.copy(output_buffer)
		headers = {
			"Authorization": "Client-ID 6656d64547a5031"
		}
		data = {
			"image": f,
		}
		async with self.bot.session.post("https://api.imgur.com/3/image", data=data, headers=headers) as r:
    			link = (await r.json())["data"]["link"]

		await ctx.send(f"Imgur Link for `{ctx.prefix}background`\n<{link}>", file=discord.File(fp=output_buffer, filename="GeneratedProfile.png"))


def setup(bot):
	bot.add_cog(Patreon(bot))
