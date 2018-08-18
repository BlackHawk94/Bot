from datetime import date, timedelta
import discord, os, random, psutil, platform, asyncio
import pkg_resources as pkg
from discord.ext import commands
from discord.ext.commands import BucketType
from cogs.help import chunks
import time
from utils.checks import *
import datetime


class Miscellaneous:

	def __init__(self, bot):
		self.bot = bot

	@commands.command(description="Let's dab!")
	async def dab(self, ctx):
		await ctx.send("No. Just no. I am a bot. What did you think?")

	@has_char()
	@commands.cooldown(1, 86400, BucketType.user)
	@commands.command(description="Get $50 per day.")
	async def daily(self, ctx):
		async with self.bot.pool.acquire() as conn:
			await conn.execute('UPDATE profile SET money=money+$1 WHERE "user"=$2;', 50, ctx.author.id)
		await ctx.send("You received your daily **$50**!")

	@commands.command(description="Bot's ping.")
	async def ping(self, ctx):
		embed = discord.Embed(title="Pong!", description=f"My current latency is {round(self.bot.latency*1000, 2)}ms", color=0xf1c60c)
		await ctx.send(embed=embed)

	@commands.command(aliases=["donate"], description="Support us!")
	async def patreon(self, ctx):
		await ctx.send(f"This bot has it's own patreon page.\n\n**Why should I donate?**\nThis bot is currently on {len(self.bot.guilds)} servers, and it is growing" \
		" fast.\nHosting this bot for all users is not easy and costs money.\nIf you want to continue using the bot or just help us, please donate a small amount.\nEven"\
		" $1 can help us.\n**Thank you!**\n\n<https://patreon.com/idlerpg>")

	@commands.command(aliases=["invite"], description="Credits!")
	async def credits(self, ctx):
		await ctx.send(f"You are running version **{self.bot.version}** by Adrian.\nInvite me! " \
		f"<https://discordapp.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot&permissions=8>")

	@commands.command(description="Get some help!")
	async def support(self, ctx):
		await ctx.send("Got problems or feature requests? Join the support server:\nhttps://discord.gg/axBKXBv")

	@commands.command(aliases=["downtime"], description="Is the bot down?")
	async def down(self, ctx):
		owner = (await self.bot.application_info()).owner
		await ctx.send(f"If this bot is down, please DM me: `{owner}`")

	@commands.command(description="Some statistics.")
	async def stats(self, ctx):
		async with self.bot.pool.acquire() as conn:
			characters = await conn.fetchval('SELECT COUNT(*) FROM profile;')
			items = await conn.fetchval('SELECT COUNT(*) FROM allitems;')
		linecount = 0
		with open("idlerpg.py", encoding="utf-8") as f:
			linecount += len(f.readlines())
		for afile in os.listdir("cogs"):
			if os.path.isdir(afile) or not afile.endswith(".py"):
				continue
			with open(f"cogs/{afile}", encoding="utf-8") as f:
				linecount += len(f.readlines())
		total_online = len({m.id for m in self.bot.get_all_members() if m.status is discord.Status.online})
		total_idle = len({m.id for m in self.bot.get_all_members() if m.status is discord.Status.idle})
		total_dnd = len({m.id for m in self.bot.get_all_members() if m.status is discord.Status.dnd})
		total_offline = len({m.id for m in self.bot.get_all_members() if m.status is discord.Status.offline})
		d0 = date(2018, 3, 17)
		d1 = date.today()
		delta = d1 - d0
		myhours = delta.days*3
		sysinfo = platform.linux_distribution()
		owner = (await self.bot.application_info()).owner
		embed = discord.Embed(title="IdleRPG Statistics", colour=0xb8bbff, url=self.bot.BASE_URL, description="Official Support Server Invite: https://discord.gg/MSBatf6")
		embed.set_thumbnail(url=self.bot.user.avatar_url)
		embed.set_footer(text=f"IdleRPG {self.bot.version} | By {owner}", icon_url=self.bot.user.avatar_url)
		embed.add_field(name="General Statistics", value=f"<:online:313956277808005120>{total_online}<:away:313956277220802560>{total_idle}<:dnd:313956276893646850>" \
		 f"{total_dnd}<:offline:313956277237710868>{total_offline}", inline=False)
		embed.add_field(name="Hosting Statistics", value=f"CPU Usage: **{psutil.cpu_percent()}%**\nRAM Usage: **{psutil.virtual_memory().percent}%**\nPython Version" \
		 f" **{platform.python_version()}** <:python:445247273065250817>\ndiscord.py Version **{pkg.get_distribution('discord.py').version}**\nOperating System: " \
		 f"**{sysinfo[0].title()} {sysinfo[1].title()}**", inline=False)
		embed.add_field(name="Bot Statistics", value=f"Code lines written: **{linecount}**\nShards: **{len(self.bot.shards)}**\nServers: **{len(self.bot.guilds)}**\nMembers: " \
		 f"**{len(self.bot.users)}**\nChannels: **{len(set(self.bot.get_all_channels()))}**\nCharacters: **{characters}**\nItems: **{items}**\nAverage hours of work: " \
		 f"**{myhours}**", inline=False)
		await ctx.send(embed=embed)

	@commands.command(description="Rolls a random number. The only argument defines the maximum result")
	async def roll(self, ctx, maximum: int):
		await ctx.send(f":1234: You rolled **{random.randint(0,maximum)}**, {ctx.author.mention}!")

	@commands.command(description="Latest updates.")
	async def changelog(self, ctx):
		await ctx.send("""
**Version 3.1 released!** <:idlerpg:453946311524220949>

**What's new?**
- We started with multiprocessing and are on a good way
- Admins can give/remove XP by using `$adminxp`
- `$makebackground` now automatically generates a link to Imgur
- `$merchall` merches all items except the equipped ones for their value
- `$merge` merges two similar items and increases the first one's stat by 1
- Activeadventures are less spammy and you get 20 HP after defeating an enemy
- `$timers` lists all cooldowns, if there are negative ones, don't worry, we're on it
- Death causes are reworked due to criticism
- `$spoil` increases someone's love score, `$lovescore` shows it and `$lovers` show the best love scored people

**What's fixed?**
- Every single bug reported as far as I read them

**What will come up soon?**
- We are finishing multiprocessing 
- Some stuff regarding maybe music and more adventures and higher item stats
""")

	@commands.has_permissions(manage_messages=True)
	@commands.command(description="Clears X messages.")
	async def clear(self, ctx, num: int, target: discord.Member=None):
		if num > 1000 or num < 0:
			return await ctx.send("Invalid amount. Maximum is 1000.")
		def msgcheck(amsg):
			if target:
				return amsg.author.id==target.id
			return True
		await ctx.channel.purge(limit=num, check=msgcheck)
		await ctx.send(f'👍 Deleted **{num}** messages for you.', delete_after=10)

	@commands.command(name="8ball", description="A usual 8ball...")
	async def _ball(self, ctx, *, question: str):
		results = ["It is certain"," It is decidedly so","Without a doubt","Yes, definitely","You may rely on it","As I see it, yes"," Most likely","Outlook good","Yes","Signs point to yes"," Reply hazy try again","Ask again later","Better not tell you now","Cannot predict now","Concentrate and ask again","Don't count on it","My reply is no","My sources say no","Outlook not so good","Very doubtful"]
		await ctx.send(f"The :8ball: says: **{random.choice(results)}**.")

	@commands.command(aliases=["say"], description="Echo! Echo....")
	async def echo(self, ctx, *, shout: str):
		try:
			await ctx.message.delete()
		except:
			pass
		shout = await commands.clean_content().convert(ctx, shout)
		await ctx.send(f"{shout}")

	@commands.command(description="A usual guess...")
	async def choose(sef, ctx, *results: commands.clean_content):
		await ctx.send(f"My choice is: **{random.choice(results)}**.")

	@commands.command(description="A usual love test...")
	async def love(self, ctx, first: discord.Member, second: discord.Member):
		msg = await ctx.send(embed=discord.Embed(description=f"Calculating Love for {first.mention} and {second.mention}...", color=0xff0000))
		await asyncio.sleep(5)
		random.seed(int(str(first.id)+str(second.id)))
		if first == second:
			love = 100.00
		else:
			love = random.randint(1, 10000)/100
		embed=discord.Embed(title="Love Calculation", description=f"Love for {first.mention} and {second.mention} is at **{love}%**! ❤", color=0xff0000)
		await msg.edit(embed=embed)

	@commands.command(description="Fancy Text")
	async def fancy(self, ctx, *, text: str):
		nums = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
		newtext = ""
		for letter in text:
			if letter.lower() in list(map(chr, range(97, 123))):
				newtext += f":regional_indicator_{letter.lower()}:"
			elif letter in [str(anum) for anum in range(10)]:
				newtext += f":{nums[int(letter)]}:"
			else:
				newtext += letter
		await ctx.send(newtext)

	@commands.command(description="Memes :)")
	async def meme(self, ctx):
		async with self.bot.session.get(f"https://some-random-api.ml/meme?lol={random.randint(1,1000000)}") as resp:
			await ctx.send(embed=discord.Embed(color=0x0a00ff).set_image(url=(await resp.json())["url"]))

	@commands.command(description="Roleplay dice. Uses ndx format.")
	async def dice(self, ctx, type: str):
		type = type.lower().split("d")
		if len(type)!=2:
			return await ctx.send("Use the ndx format.")
		try:
			type[0] = int(type[0])
			type[1] = int(type[1])
			if type[0] > 100:
				return await ctx.send('Too many dices.')
		except:
			await ctx.send("Use the ndx format.")
		results = []
		for i in range(type[0]):
			results.append(random.randint(1, type[1]))
		sumall = 0
		for i in results:
			sumall += i
		average = sumall / len(results)
		nl = "\n"
		results = [str(result) for result in results]
		await ctx.send(f"```Sum: {sumall}\nAverage: {average}\nResults:\n{nl.join(results)}```")

	@commands.command(description="What am I called where?")
	async def randomname(self, ctx):
		g = random.choice([g for g in self.bot.guilds if g.me.display_name != self.bot.user.name])
		info =  (g.me.display_name, g.name)
		await ctx.send(f"In **{info[1]}** I am called **{info[0]}**.")

	@commands.command(description="Cats!")
	async def cat(self, ctx):
		await ctx.send(embed=discord.Embed(title="Meow!", color=ctx.author.color.value).set_image(url=f"http://thecatapi.com/api/images/get?results_per_page=1&anticache={random.randint(1,10000)}"))

	@commands.command(description="Dogs!")
	async def dog(self, ctx):
		async with self.bot.session.get("https://api.thedogapi.com/v1/images/search") as r:
			res = await r.json()
		await ctx.send(embed=discord.Embed(title="Wouff!", color=ctx.author.color.value).set_image(url=res[0]['url']))

	@commands.command(description="Bot uptime.")
	async def uptime(self, ctx):
		p = psutil.Process(os.getpid())
		secs = int(time.time() - p.create_time())
		await ctx.send(f"I am online for **{str(timedelta(seconds=secs))}**.")


	@commands.command(hidden=True)
	async def easteregg(self, ctx):
		await ctx.send("Find it!")

	@commands.command(description="Support server notifications.")
	async def notifyme(self, ctx):
		if not ctx.guild.id==430017996304678923:
			return await ctx.send("Support Server Only")
		role = [r for r in ctx.guild.roles if r.name=="Notify"][0]
		await ctx.author.add_roles(role)
		await ctx.send("Notifications triggered.")

	@commands.command(description="Turn off support server notifications.")
	async def unnotifyme(self, ctx):
		if not ctx.guild.id==430017996304678923:
			return await ctx.send("Support Server Only")
		role = [r for r in ctx.guild.roles if r.name=="Notify"][0]
		await ctx.author.remove_roles(role)
		await ctx.send("Notifications disabled.")

	@commands.command(description="Gives a cookie to a user.")
	@commands.guild_only()
	@commands.cooldown(1.0, 20.0, BucketType.user)
	async def cookie(self, ctx, user: discord.Member):
		await ctx.send(f"**{user.display_name}**, you've been given a cookie by **{ctx.author.display_name}**. :cookie:")

	@commands.command(description="Ice Cream!", aliases=["ice-cream"])
	async def ice(self, ctx, other:discord.Member):
		await ctx.send(f"{other.mention}, here is your ice: :ice_cream:!")

	@commands.command(description="Traven!")
	async def traven(self, ctx):
		await ctx.send(random.choice(["He is great!", "He is an asshole!", "Maybe he is cool.", "I like him", "I don't like him.", "He's a god!"]))

	@commands.cooldown(1, 10, BucketType.channel)
	@commands.command(description="User guessing game.")
	async def guess(self, ctx):
		m = random.choice(ctx.guild.members)
		em = discord.Embed(title="Can you guess who this is?", description=f"Their discriminant is `#{m.discriminator}`", color=m.color)
		em.set_image(url=m.avatar_url)
		await ctx.send(embed=em)
		def check(msg):
			return (msg.content == m.name or msg.content == str(m)) and msg.channel == ctx.channel

		try:
			msg = await self.bot.wait_for("message", check=check, timeout=10)
		except:
			return await ctx.send(f"You didn't guess correctly! It was `{m}`!")
		await ctx.send(f"{msg.author.mention}, you are correct!")

	@commands.command(description="Lists all your cooldowns.", aliases=["cooldowns"])
	async def timers(self, ctx):
		res = "```\n"
		for c in set(self.bot.walk_commands()):
			if c._buckets._cache.get(ctx.author.id):
				time = c._buckets._cache.get(ctx.author.id)._window
				time = datetime.timedelta(seconds=c._buckets._cache.get(ctx.author.id).per) - (datetime.datetime.utcnow() - datetime.datetime.fromtimestamp(time))
				if str(time).split('.')[0].startswith("-"):
					continue
				res += f"{c.name} is on cooldown and available in {str(time).split('.')[0]}\n"
		res += "```"
		await ctx.send(res)

	@commands.command(description="Ask me a yes/no question.", aliases=["yn"])
	async def yesno(self, ctx, *, question: str):
		async with self.bot.session.get("http://gelbpunkt.troet.org/api/") as r:
			res = await r.json()
		em = discord.Embed(title=question, description=res.get("result"), colour=ctx.author.colour)
		em.set_thumbnail(url=ctx.author.avatar_url)
		em.timestamp = datetime.datetime.strptime(res.get("time"), '%Y-%m-%dT%H:%M:%SZ')
		await ctx.send(embed=em)

	@commands.command(description="View IdleRPG's partnered bots.")
	async def partners(self, ctx):
		em = discord.Embed(title="Partnered Bots", description="Awesome bots made by other people!", colour=discord.Colour.blurple())
		em.add_field(name="GamesROB", value="Trivia, Hangman, Minesweeper, Connect 4 and more, right from your chat! A bot offering non-RPG games made by deprilula28 and Fin.\n[discordbots.org Page](https://discordbots.org/bot/gamesrob)")
		await ctx.send(embed=em)

def setup(bot):
	bot.add_cog(Miscellaneous(bot))
