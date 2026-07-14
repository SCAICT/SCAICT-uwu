"""
For Build.
"""

# Third-party imports
import discord
import discord.ext.commands


class Build(discord.ext.commands.Cog):
    """
    Attributes:
        bot (discord.Bot): Instance of discord.Bot.
    """

    bot: discord.Bot
    """
    bot (discord.Bot): Instance of discord.Bot.
    """

    def __init__(self, bot: discord.Bot) -> None:
        """
        Constructor function.

        Parameters:
            bot (discord.Bot): Instance of discord.Bot.
        """
        self.bot = bot
