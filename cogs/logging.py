import discord
from discord.ext import commands
import asyncio
from cogs.utils import settings
from cogs.utils import permissions
import datetime

class Logging:
    def __init__(self, loggy):
        self.loggy = loggy
    
    async def on_member_remove(self, member):
        # When a user is removed from the server.
        log_message = u"{} Left the server!".format(member.name)
        await self.loggy.send_message(self.loggy.get_channel(settings.get_settings(member.server.id)["log-channels"]["general"]), log_message)
        settings.log(member.server.id, "general", log_message)
        
    async def on_member_join(self, member):
        # When a user is registered with a server
        log_message = u"{} Joined the server!".format(member.name)
        welcome_str = settings.get_settings(member.server.id).get("welcome-messge", u"Welcome to {} {}!")
        await self.loggy.send_message(member, welcome_str.format(member.server.name,member.name))
        await self.loggy.send_message(self.loggy.get_channel(settings.get_settings(member.server.id)["log-channels"]["general"]), log_message)
        settings.log(member.server.id, "general", log_message)
    
    async def on_member_ban(self, member):
        log_message = u"{} Was banned from {}!".format(member.name,member.server)
        await self.loggy.send_message(self.loggy.get_channel(settings.get_settings(member.server.id)["log-channels"]["general"]), log_message)
        settings.log(member.server.id, "audit", log_message)
    
    async def on_voice_state_update(self, before, after):
        # Triggered on channel change and mute/deafen
        if before.bot:
            return
        if(before.voice_channel == after.voice_channel):
            return
        elif(after.voice_channel is None):
            message = u'{0} Disconnected from {1}'
            channel = before.voice_channel
            settings.log(before.server.id, "general", u'{0} Disconnected from {1}'.format(before.name,channel.name))
        else:
            message = u'{0} Moved to {1}'
            channel = after.voice_channel
            settings.log(before.server.id, "general", message.format(before.name,channel.name))
        await self.loggy.send_message(self.loggy.get_channel(settings.get_settings(before.server.id)["log-channels"]["general"]),message.format(before.name,channel.name))
   
    async def on_member_update(self, before, after):
        if before.bot:
            return
        # Nickname Changes
        if before.nick != after.nick:
            if after.nick is None:
                message = "{0} Reset their nickname"
                await self.loggy.send_message(self.loggy.get_channel(settings.get_settings(before.server.id)["log-channels"]["general"]), message.format(before.name))
                settings.log(before.server.id, "general", u"{0} changed reset their nickname".format(before.name)) 
            else:
                message = "{0} Changed their nickname to {1}"
                await self.loggy.send_message(self.loggy.get_channel(settings.get_settings(before.server.id)["log-channels"]["general"]), message.format(before.name, after.nick))
                settings.log(before.server.id, "general", u"{0} changed their nickname to {1}".format(before.name,after.nick))
        # Status Changes
        """ This is pretty spammy so it can be enabled and disabled in the settings or with the logs_toggle command """
        if settings.get_settings(before.server.id)["enabled_logs"]["status"] == "on":
            if before.status != after.status:
                message = "{0}'s status changed to {1}"
                await self.loggy.send_message(self.loggy.get_channel(settings.get_settings(before.server.id)["log-channels"]["status"]), message.format(before.name, after.status))
        if settings.get_settings(before.server.id)["enabled_logs"]["games"] == "on":
            if before.game != after.game:
                if after.game is None:
                    message = "{0} Has stopped playing {1}"
                    await self.loggy.send_message(self.loggy.get_channel(settings.get_settings(before.server.id)["log-channels"]["games"]), message.format(before.name, before.game))
                else:
                    message = "{0} Is now playing {1}"
                    await self.loggy.send_message(self.loggy.get_channel(settings.get_settings(before.server.id)["log-channels"]["games"]), message.format(before.name, after.game))

            
def setup(loggy):
    loggy.add_cog(Logging(loggy))
    