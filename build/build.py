"""
For Build.
"""

# Third-party imports
from discord import Bot
from discord.ext.commands import Cog

class Build(Cog):
    """
    Attributes:
        bot (Bot): Instance of discord.Bot.
    """

    bot: Bot
    """
    bot (Bot): Instance of discord.Bot.
    """

    def __init__(self, bot: Bot) -> None:
        """
        Constructor function.

        Parameters:
            bot (Bot): Instance of discord.Bot.
        """
        self.bot = bot
