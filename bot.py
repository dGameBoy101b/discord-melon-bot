import discord
import sys
import os
from dotenv import load_dotenv
import logger

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
LOG_FOLDER = os.getenv('MELON_BOT_LOGS')
BACK_LIMIT = 200
DM_BACK_LIMIT = 10
TRIGGER_BACK_LIMIT = 500
BACK_TRIGGER = 'melon'
MELON = '\U0001f349'
PERMISSIONS_MESSAGE = ('To function I require the permision to add reactions.\n'
                       +'If you want me to update previously existing messages, I need permission to read the message history too.')

class MelonBotClient(discord.Client):
    async def melon_reaction(self, message):
            try:
                await message.add_reaction(MELON)
                logger.info(f'Added melon to message in the guild {message.guild}, in the text channel {message.channel}')
            except discord.errors.Forbidden:
                logger.warning(f'Could not add melon to message in the guild {message.guild}, in the text channel {message.channel}!')

    async def melon_back_check_channel(self, channel, back_limit=BACK_LIMIT):
        if BACK_LIMIT > 0:
            logger.debug(f'Checking for melons in the text channel {channel}')
            try:
                async for message in channel.history(limit=back_limit):
                    if message.author != client.user:
                        for reaction in message.reactions:
                            if not reaction.me and reaction.emoji == MELON:
                                await self.melon_reaction(message)
                                break
                        else:
                            await self.melon_reaction(message)
                logger.debug(f'Finished checking for melons in the text channel {channel}, in the guild {channel.guild}')
                            
            except discord.errors.Forbidden:
                logger.warning(f'Could not check for melons in the guild {channel.guild}, in the text channel {channel}!')

    async def melon_back_check_guild(self, guild):
        if BACK_LIMIT > 0:
            logger.debug(f'Checking for melons in the guild {guild} in the last {BACK_LIMIT} messages')
            for channel in guild.text_channels:
                await self.melon_back_check_channel(channel)
            logger.debug(f'Finshed checking for melons in the guild {guild}')

    async def melon_permission_dm(self, guild):
        if guild.owner != client.user:
            if guild.owner.dm_channel == None:
                await guild.owner.create_dm()
            dm = guild.owner.dm_channel
            if DM_BACK_LIMIT >= 0:
                try:
                    async for message in dm.history(limit=DM_BACK_LIMIT):
                        if message.author == client.user:
                            logger.debug(f'{guild.owner} already knows about my permissions for their guild \'{guild}\'')
                            return
                except discord.errors.Forbidden:
                    logger.warning(f'Could not read dm history with {guild.owner}')
            try:
                if DM_EXPIRE > 0:
                    await dm.send(PERMISSIONS_MESSAGE, delete_after=DM_EXPIRE)
                else:
                    await dm.send(PERMISSIONS_MESSAGE)
                logger.info(f'permissions dm sent to {guild.owner} for their guild {guild}')
            except discord.errors.Forbidden:
                logger.warning(f'{guild.owner} refused to recieve the permissions dm for their guild {guild}!')
                      
    async def on_connect(self):
        logger.debug('This bot is in guilds with the following ids:')
        for guild in client.guilds:
            logger.debug(f'{guild.id}')
        logger.debug(f'{BACK_LIMIT} messages will be back checked for melons')
        
    async def on_guild_available(self, guild):
        logger.debug(f'{guild} became available')
        await self.melon_back_check_guild(guild)
                
    async def on_message(self, message):
        channel = message.channel
        if isinstance(channel, discord.TextChannel):
            logger.debug(f'{message.author} has posted in the guild {message.guild}, in the text channel {channel}')
        else:
            logger.debug(f'{message.author} has posted a message!')
        if message.author != client.user:
            await self.melon_reaction(message)
        if BACK_TRIGGER.lower() in message.content.lower():
            logger.info(f'melon back check triggered in the guild {message.guild}, in the text channel {message.channel}')
            await self.melon_back_check_channel(message.channel, TRIGGER_BACK_LIMIT)

    async def on_guild_join(self, guild):
        await self.melon_permission_dm(guild)

logger = logger.initialise_logger(LOG_FOLDER, __name__)
client = MelonBotClient()
client.run(TOKEN)
