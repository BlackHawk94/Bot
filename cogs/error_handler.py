from datetime import timedelta
import discord, traceback
from discord.ext import commands
import Levenshtein as lv
import utils.checks
import sys

class Errorhandler:
    def __init__(self, bot):
        self.bot = bot
        bot.on_command_error = self._on_command_error
        bot.on_error = self._on_error

    async def _on_error(self, event, *args, **kwargs):
        message = args[0] #Gets the message object
        error, value = sys.exc_info()[:2]
        if isinstance(error, utils.checks.NoCharacter):
            await message.channel.send(f"You don't have a character yet. Use `{ctx.prefix}create` to create a new character!")

    async def _on_command_error(self, ctx, error, bypass = False):
        if hasattr(ctx.command, 'on_error') or (ctx.command and hasattr(ctx.cog, f'_{ctx.command.cog_name}__error')) and not bypass:
            # Do nothing if the command/cog has its own error handler and the bypass is False
            return
        if isinstance(error, commands.CommandNotFound):
            async with self.bot.pool.acquire() as conn:
                try:
                    ret = await conn.fetchval('SELECT "unknown" FROM server WHERE "id"=$1;', ctx.guild.id)
                except:
                    return
            if not ret:
                return
            nl = "\n"
            matches = []
            for command in list(self.bot.commands):
                if lv.distance(ctx.invoked_with, command.name) < 4:
                    matches.append(command.name)
            if len(matches) == 0:
                matches.append("Oops! I couldn't find any similar Commands!")
            try:
                await ctx.send(f"**`Unknown Command`**\n\nDid you mean:\n{nl.join(matches)}\n\nNot what you meant? Type `{ctx.prefix}help` for a list of commands.")
            except:
                pass
        elif hasattr(error, 'original') and isinstance(getattr(error, 'original'), utils.checks.NoCharacter):
            await ctx.send(f"You don't have a character yet. Use `{ctx.prefix}create` to create a new character!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Oops! You forgot a required argument: `{error.param.name}`")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"You used a wrong argument!")
        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(f"You are on cooldown. Try again in {timedelta(seconds=int(error.retry_after))}.")
        elif isinstance(error, discord.Forbidden):
            pass
        elif isinstance(error, commands.NotOwner):
            await ctx.send(embed=discord.Embed(title="Permission denied", description=":x: This command is only avaiable for the bot owner.", colour=0xff0000))
        elif isinstance(error, commands.CheckFailure):
            if type(error) == utils.checks.NoCharacter:
                return await ctx.send("You don't have a character yet.")
            await ctx.send(embed=discord.Embed(title="Permission denied", description=":x: You don't have the permissions to use this command. It is thought for other users.", \
             colour=0xff0000))
        elif isinstance(error, discord.HTTPException):
            await ctx.send(f"There was a error responding to your message:\n`{error.text}`\nCommon issues: Bad Guild Icon or too long response")
        elif isinstance(error, commands.CommandInvokeError) and hasattr(error, 'original'):
            print('In {}:'.format(ctx.command.qualified_name), file=sys.stderr)
            traceback.print_tb(error.original.__traceback__)
            print('{0}: {1}'.format(error.original.__class__.__name__, error.original), file=sys.stderr)
        else:
            print(traceback.format_exc())
        try:
            ctx.command.reset_cooldown(ctx)
        except:
            pass

def setup(bot):
	bot.add_cog(Errorhandler(bot))
