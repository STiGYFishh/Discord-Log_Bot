import discord
from discord.ext import commands
import asyncio
import importlib
import datetime
import time
import traceback
import sys
import os
from cogs.utils import settings
from cogs.utils import permissions

startup_extensions = ["cogs.commands", "cogs.logging"]
token = input("Please input Auth Token: ")
chosen_prefix = input("Please choose a command prefix (e.g ?): ")

description = """ A terribly written, simple logging bot by STiGYFishh """
loggy = commands.Bot(command_prefix=commands.when_mentioned_or(chosen_prefix), description=description)

@loggy.event
async def on_message(message):
    if message.author.bot:
        return
    
    await loggy.process_commands(message)
    
@loggy.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.NoPrivateMessage):
        await loggy.send_message(ctx.message.author, "Sorry. This command is unavailable in PM's")
    elif isinstance(error, commands.DisabledCommand):
        await loggy.send_message(ctx.message.author, "Sorry. This command is disabled and cannot be used.")
    elif isinstance(error, commands.CheckFailure):
        if error.args[0] == "Cannot Process Actions; General Logs Channel not set!":
            await loggy.send_message(ctx.message.author, error)
        else:
            await loggy.send_message(ctx.message.author, "You do not have permission to use this command. This incident has been logged.")
            settings.log(ctx.message.server.id, "audit", "{} tried to execute command {} but failed the permissions check!".format(ctx.message.author,ctx.command.qualified_name))
    elif isinstance(error, commands.CommandInvokeError):
        print("In {0.command.qualified_name}:".format(ctx), file=sys.stderr)
        traceback.print_tb(error.original.__traceback__)
        print("{0.__class__.__name__}: {0}".format(error.original), file=sys.stderr)
 
@loggy.command()
@permissions.are_you_my_mummy() 
async def load(ctx, name: str):
        """Loads a cog."""
        cog_name = "cogs.{0}".format(name)
        cog_settings = settings.get_cogs()
        if cog_name not in list(loggy.extensions):
            try:
                cog = importlib.import_module(cog_name)
                importlib.reload(cog)
                loggy.load_extension(cog.__name__)
                cog_settings.append(cog_name)
                settings.save_cogs(cog_settings)
                await loggy.say("`{0}` loaded successfully.".format(name))
            except Exception as e:
                _traceback = traceback.format_tb(e.__traceback__)
                _traceback = ''.join(_traceback[2:])
                await loggy.say('Unable to load; the cog caused a `{0}`:\n```py\nTraceback '
                                     '(most recent call last):\n{1}{0}: {2}\n```'
                                     .format(type(e).__name__, _traceback, e))
        else:
            await loggy.say('Unable to load; that cog is already loaded.')
            
@loggy.command()
@permissions.are_you_my_mummy()
async def reload(name: str):
    """Reloads a cog."""
    cog_name = "cogs.{0}".format(name)
    if cog_name in list(loggy.extensions):
        cog = importlib.import_module(cog_name)
        importlib.reload(cog)
        loggy.unload_extension(cog_name)
        loggy.load_extension(cog_name)
        await loggy.say("`{0}` reloaded successfully.\nLast modified at: `{1}`"
                             .format(name, datetime.datetime.fromtimestamp(os.path.getmtime(cog.__file__))))
    else:
        await loggy.say("Unable to reload, that cog isn\'t loaded.")

@loggy.command()
@permissions.are_you_my_mummy()
async def unload(name: str):
    """Unloads a cog."""
    cog_name = "cogs.{0}".format(name)
    cog_settings = settings.get_cogs()
    if cog_name in list(loggy.extensions):
        loggy.unload_extension(cog_name)
        cog_settings.remove(cog_name)
        settings.save_cogs(cog_settings)
        await loggy.say("`{0}` unloaded successfully.".format(name))
    else:
        await loggy.say("Unable to unload; that cog isn\'t loaded.")
    
@loggy.command(alaises=["halt"])
@permissions.are_you_my_mummy()
async def shutdown():
    """ Shutdown the bot """
    loggy.logout
    
@loggy.event
async def on_server_join(server):
    print("Bot was added to {} : {}".format(server.id, server.name))
    await settings.check_servers(loggy)

@loggy.event
async def on_ready():
    await settings.check_servers(loggy)
    print("\n ( --- Log Bot Version 0.1.1 --- )")
    print("      Connected as: " + loggy.user.name)
    print("      ID: " + loggy.user.id)
    print(" ")
    await asyncio.sleep(1)

 
if __name__ == "__main__":
    print("\n Starting Loggy the Log Bot \n Loading Cogs and Logging into Discord... \n")
    time.sleep(3)
    cog_settings = []
    for extension in startup_extensions:
        try:
            print(" Loading {0}...".format(extension))
            loggy.load_extension(extension)
            time.sleep(1)
            cog_settings.append(extension)
            settings.save_cogs(cog_settings)
            time.sleep(1)
            print(" Successfully loaded {0} \n".format(extension))
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print(" Failed to load extension {}\n{}".format(extension, exc))

    loggy.run(token)