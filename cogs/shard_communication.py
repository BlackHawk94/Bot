import json
import discord
from discord.ext import commands
from datetime import timedelta

# Cross-process cooldown check (pass this to commands)
def user_on_cooldown(cooldown: int):
    async def predicate(ctx):
        command_ttl = await ctx.bot.redis.execute("TTL", f"cd:{ctx.author.id}:{ctx.command.name}")
        if command_ttl == -2:
            await ctx.bot.redis.execute("SET", f"cd:{ctx.author.id}:{ctx.command.name}", ctx.command.name, "EX", cooldown)
            return True
        else:
            raise commands.CommandOnCooldown(ctx, command_ttl)
            return False
    return commands.check(predicate) # TODO: Needs a redesign

def dict_to_kwargs(**kwargs):
    return ', '.join('%s=%r' % x for x in kwargs.items())

class GuildCommunication:
    def __init__(self, bot):
        self.bot = bot
        self.communication_channel = 'guild-channel'
        self.handler = None
        bot.loop.create_task(self.register_sub())

    async def register_sub(self):
        if not self.communication_channel in self.bot.redis.pubsub_channels:
            await self.bot.redis.execute_pubsub('SUBSCRIBE', self.communication_channel)
            self.handler = self.bot.loop.create_task(self.event_handler())

    async def unregister_sub(self):
        await self.bot.redis.execute_pubsub('UNSUBSCRIBE', self.communication_channel)

    async def event_handler(self):
        channel = self.bot.redis.pubsub_channels[self.communication_channel]
        while await channel.wait_message():
            try:
                payload = await channel.get_json(encoding="utf-8")
            except json.decoder.JSONDecodeError:
                return # not a valid JSON message
            if payload.get('action') and hasattr(self, payload.get('action')):
                try:
                    eval(f"self.bot.loop.create_task(self.{payload.get('action')}({dict_to_kwargs(**payload.get('args'))}))")
                except Exception as e:
                    print(e)

    async def send_message(self, channel_id: int, message: str):
        await self.bot.get_channel(channel_id).send(message)

    async def guild_count(self, command_id: int):
        payload = {'command_id': command_id, 'guildcount': len(self.bot.guilds)}
        await self.bot.redis.execute('PUBLISH', self.communication_channel, json.dumps(payload))

    async def reload_cog(self, cog_name: str):
        if cog_name in self.bot.cogs:
            try:
                self.bot.unload_extension(cog_name)
            except Exception as e:
                print(e)
                return
        try:
            self.bot.load_extension(cog_name)
        except Exception as e:
            await self.bot.redis.execute('PUBLISH', self.communication_channel, json.dumps({'status': 'error', 'error_message': str(e)}))
            return
        await self.bot.redis.execute('PUBLISH', self.communication_channel, json.dumps({'status': 'Done'}))

    async def load_cog(self, cog_name: str):
        try:
            self.bot.load_extension(cog_name)
        except Exception as e:
            await self.bot.redis.execute('PUBLISH', self.communication_channel, json.dumps({'status': 'error', 'error_message': str(e)}))
            return
        await self.bot.redis.execute('PUBLISH', self.communication_channel, json.dumps({'status': 'Done'}))

    async def unload_cog(self, cog_name: str):
        if cog_name in self.bot.cogs:
            try:
                self.bot.unload_extension(cog_name)
            except Exception as e:
                await self.bot.redis.execute('PUBLISH', self.communication_channel, json.dumps({'status': 'error', 'error_message': str(e)}))
                return
        await self.bot.redis.execute('PUBLISH', self.communication_channel, json.dumps({'status': 'Done'}))

    @user_on_cooldown(cooldown=20)
    @commands.command()
    async def diniboytestwontexecuteit(self, ctx):
        await ctx.send("I said, don't! :\\")

    def __unload(self):
        self.bot.loop.create_task(self.unregister_sub())
        self.handler.cancel()

def setup(bot):
    bot.add_cog(GuildCommunication(bot))
