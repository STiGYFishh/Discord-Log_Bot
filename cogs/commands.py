import discord
from discord.ext import commands
import asyncio
import codecs
import traceback
from cogs.utils import permissions
from cogs.utils import settings

class Commands:
    def __init__(self, loggy):
        self.loggy = loggy

    @commands.command(pass_context=True)
    @permissions.has_permission()
    @permissions.is_setup()
    async def check(self ,ctx):
        """ Sends a check message for testing purposes """
        await self.loggy.say("Check")
        await self.loggy.send_message(self.loggy.get_channel(settings.get_settings(ctx.message.server.id)["log-channels"]["general"]), "Check")
 
    # Admin Commmand Group.
    @commands.group(pass_context=True)
    @permissions.has_permission()
    async def admin(self, ctx):
        """ Allows you to add, remove or list current Administrators of this bot. """
        pass 
    
    @admin.command(pass_context=True)
    async def add(self, ctx, id: str):
        """ Add a user to the Bot administrator list *Logged Action* """
        setup, reqs = permissions.is_setup(ctx)
        if not setup:   
            await self.loggy.say(reqs)
            return False
        try:
            new_admin = ctx.message.server.get_member(id)
        except:
            await self.loggy.say("Something raised an exception...")
            return
        await self.loggy.send_message(ctx.message.author, 
                                        "Are you sure you want to give {0.mention} administrator rights? \n Please type"
                                        " 'I want to give {1} administrator rights'".format(new_admin, new_admin))

        def check(check_message):
            return check_message.content == ("I want to give {0} administrator rights".format(new_admin))
            
        check_message = await self.loggy.wait_for_message(author=ctx.message.author, check=check)  
        settings.save_setting(ctx.message.server.id, "admins", new_admin.display_name, id) 
        result = u"{0.name} Has been given administrator privileges by {1.name}".format(new_admin,ctx.message.author)
        settings.log(ctx.message.server.id, "audit", result)
        await self.loggy.send_message(self.loggy.get_channel(settings.get_settings(ctx.message.server.id)["log-channels"]["general"]), result)

    @admin.command(pass_context=True)
    async def remove(self, ctx, id: str):
        """ Remove a user from the Bot administrator list *Logged Action* """
        setup, reqs = permissions.is_setup(ctx)
        if not setup:   
            await self.loggy.say(reqs)
            return False
        try:
            to_remove = ctx.message.server.get_member(id)
        except:
            await self.loggy.say("Invalid User ID given.")
            return
        await self.loggy.send_message(ctx.message.author, 
                                        "Are you sure you want to remove {0.mention}'s administrator rights? \n Please type"
                                        " 'I want to remove {1}'s administrator rights'".format(to_remove, to_remove))

        def check(check_message):
            return check_message.content == ("I want to remove {0}'s administrator rights".format(to_remove))
            
        check_message = await self.loggy.wait_for_message(author=ctx.message.author, check=check)  
        settings.remove_setting(ctx.message.server.id, "admins", to_remove.display_name) 
        result = u"{0.name} Has been stripped of administrator privileges by {1.name}".format(to_remove,ctx.message.author)
        settings.log(ctx.message.server.id, "audit", result)
        await self.loggy.send_message(self.loggy.get_channel(settings.get_settings(ctx.message.server.id)["log-channels"]["general"]), result)
        
    @admin.command(pass_context=True)
    async def list(self, ctx):
        """ List current users in the Bot's administrator list """
        admin_list = settings.get_settings(ctx.message.server.id)["admins"]
        message = u""
        for k,v in admin_list.items():
            message += k + " : " + v + "\n"
        embed_message = discord.Embed(title='Administrators:', description=message, colour=0xDEADBF)
        await self.loggy.send_message(ctx.message.channel,embed=embed_message)
        
    @commands.command(pass_context=True, name="purgelog", aliases=["p_log"])
    @permissions.has_permission()
    async def purge_log(self, ctx, amount: int):
        """ Removes specified number of log messages from the logs channel """
        await self.loggy.send_message(ctx.message.channel, "Are you sure you want to purge the logs? "
                                                    "\n Type 'Confirm' to proceed.")
        def check(message):
            return message.content.startswith("Confirm")

        message = await self.loggy.wait_for_message(author=ctx.message.author, check=check)

        def is_log_bot(message):
            return message.author == self.loggy.user

        deleted = await self.loggy.purge_from(self.loggy.get_channel(settings.get_settings(ctx.message.server.id)["log-channels"]["general"]),limit=amount, check=is_log_bot)
        await self.loggy.send_message(message.channel, "Deleted {} message(s)".format(len(deleted)))
        settings.log(ctx.message.server.id, "audit", u"{0.name} Deleted {1} log message(s) \n".format(ctx.message.author,len(deleted)))
        
    @commands.command(pass_context=True, name="welcome_msg", aliases=["wmsg","welcomemsg"])
    @permissions.has_permission()
    async def change_welcome_str(self, ctx, *message):
        """ Changes the welcome message a new member recieves when joining the server. \n\nOptions:\n'--name--' Can be used to insert the username. \n '--server--' Can be used to insert the servername \n\nExample: '?welcome_msg Hello --name-- welcome to --server--'"""
             
        message = " ".join(message)        
        welcome_message = message.replace("--server--", "{0}").replace("--name--", "{1}")
            
        settings.save_setting(ctx.message.server.id, None, "welcome-message", welcome_message)
        await self.loggy.say("Welcome message updated! Preview: \n " + welcome_message.format(ctx.message.server.name, ctx.message.author.name))

    @commands.group(pass_context=True, name="logchannel", aliases=["logch"])
    @permissions.has_permission()
    async def log_channel(self, ctx):
        """ Allows you to change the channels that are logged to, and to enable or disable logging categories using the toggle command """
        pass
    
    @log_channel.command(pass_context=True)
    async def general(self, ctx, channel):
        """ Change the channel for general logs, takes the channel ID as an argument e.g \n `?logch general 123456789` """
        try:
            await self.loggy.send_message(self.loggy.get_channel(channel), "Testing New Log Channel...")
        except discord.Forbidden:
            await self.loggy.say("I Don't have permission to use that channel!")
            return
        except:
            await self.loggy.say("Invalid Channel ID supplied!")
            return
        finally:
            settings.save_setting(ctx.message.server.id, "log-channels", "general", channel)
            await self.loggy.say("Log channel for General logs has been updated.")                
    
    @log_channel.command(pass_context=True)        
    async def status(self, ctx, channel):
        """ Change the channel for status logs, takes the channel ID as an argument e.g \n `?logch status 123456789` """
        try:
            await self.loggy.send_message(self.loggy.get_channel(channel), "Testing New Log Channel...")
        except discord.Forbidden:
            await self.loggy.say("I Don't have permission to use that channel!")
            return
        except:
            await self.loggy.say("Invalid Channel ID supplied!")
            return
        finally:
            settings.save_setting(ctx.message.server.id, "log-channels", "status", channel)
            await self.loggy.say("Log channel for Status logs has been updated.")
    
    @log_channel.command(pass_context=True)    
    async def games(self, ctx, channel):
        """ Change the channel for game logs, takes the channel ID as an argument e.g \n `?logch games 123456789` """
        try:
            await self.loggy.send_message(self.loggy.get_channel(channel), "Testing New Log Channel...")
        except discord.Forbidden:
            await self.loggy.say("I Don't have permission to use that channel!")
            return
        except:
            await self.loggy.say("Invalid Channel ID supplied!")
            return
        finally:
            settings.save_setting(ctx.message.server.id, "log-channels", "games", channel)
            await self.loggy.say("Log channel for Games logs has been updated.")
    
    @log_channel.command(pass_context=True)    
    async def toggle(self, ctx, log, status):
        """ Change whether or not a logging category is enabled. \n\n Options are `status` and `games`. \n General cannot be disabled (Hu Doi) \n usage: `?logch toggle  status|games  on|off """
        if log == "status" or log == "games":
            if status == "on" or status == "off":
                if status == "on":
                    if settings.get_settings(ctx.message.server.id)["log-channels"][log] == "":
                        await self.loggy.say("Cannot Turn {0} Logs {1}; Log Channel has not been set!".format(log, status))
                        return False
                settings.save_setting(ctx.message.server.id, "enabled_logs", log, status)
                await self.loggy.say("Logs for {0} have been turned {1}".format(log, status))
                settings.log(ctx.message.server.id, "audit", "{0} turned {1} {2} logs".format(ctx.message.author.name, status, log))
            else:
                await self.loggy.say("That's not a valid mode! \n\n Options: \n `on` \n `off` ")
                return
        else:
            await self.loggy.say("That's not a valid log category! \n\n Options: \n `status` \n `games` ")
            return
            
    @commands.command(pass_context=True, name="setupstatus", aliases=["ss","sstatus"])
    @permissions.has_permission()
    async def setup_status(self, ctx):
        not_met = [] 
        check = settings.get_settings(ctx.message.server.id)
        for key,value in check.items():
            if value == "":
                not_met.append("{} has not been setup.".format(key))
            elif type(value) is dict:
                for subkey, subvalue in value.items():
                    if subvalue == "":
                        not_met.append("{} - {} has not been setup.".format(key, subkey))
       
        await self.loggy.say(".\n{}".format('\n'.join(not_met)))
        
def setup(loggy):
    loggy.add_cog(Commands(loggy))