import discord
from discord.ext import commands
from cogs.utils import settings

def is_setup():
    def predicate(ctx):
        if settings.get_settings(ctx.message.server.id)["log-channels"]["general"] == "":
            raise commands.CheckFailure("Cannot Process Actions; General Logs Channel not set!")
            return False
        else:
            return True
    return commands.check(predicate)
     
def are_you_my_mummy():
    def predicate(ctx):
        return ctx.message.author.id == "138622924469829632"
    
    return commands.check(predicate)

def has_permission():
    def predicate(ctx):
        server_settings = settings.get_settings(ctx.message.server.id)
        # The server owner + STiGYFishh will always have permissions.
        if ctx.message.author.id == ctx.message.server.owner.id or ctx.message.author.id == "138622924469829632":
            return True
        else:
            return ctx.message.author.id in server_settings["admins"].values()
    
    return commands.check(predicate)