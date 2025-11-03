# Standard imports
import datetime

# import subprocess
import sys
from typing import cast

# Third-party imports
import discord
from discord.ext import commands


class VersionInfo(commands.Cog):
    _SCAICT_UWU_VERSION_NUMBER: str = "0.2.0.dev0"
    """
    Current hardcoded workaround
    """

    _SCAICT_UWU_VERSION_DATE: str = "2025-11-03 (UTC)"
    """
    Current hardcoded workaround
    """

    _SCAICT_UWU_VERSION: str = (
        f"{_SCAICT_UWU_VERSION_NUMBER}\n{_SCAICT_UWU_VERSION_DATE}"
    )
    """
    Current hardcoded workaround
    """

    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    def embeds_version_info(self) -> list[discord.Embed]:
        """
        List of version information embeds.
        """

        return [
            self.embed_version_info_title(),
            self.embed_installed_software(),
            # self.embed_installed_packages(),
            self.embed_version_info_footer(),
        ]

    def embed_version_info_title(self) -> discord.Embed:
        """
        Main title embed of the version information embeds.
        """

        bot_avatar = self.bot.user.avatar

        if bot_avatar is None:
            bot_avatar = self.bot.user.default_avatar

        return discord.Embed(
            color=0xFF24CF,
            title="版本資訊",
            thumbnail=bot_avatar.url,
        )

    def embed_installed_software(self) -> discord.Embed:
        """
        == Installed software ==

        * scaict_uwu: version_num (git_hash_to-do)\\ndate
        * python
        * pip
        * mysql
        """

        embed = discord.Embed(
            color=0xFF24CF,
            title="已安裝的軟體",
        )

        # TODO: Git hash
        # process = subprocess.Popen(
        #     ['git', 'rev-parse', 'HEAD'],
        #     shell=False,
        #     stdout=subprocess.PIPE
        # )
        # git_head_hash = process.communicate()[0].strip()

        embed.add_field(
            name="中電喵",
            value=self._SCAICT_UWU_VERSION,
            inline=False,
        )
        embed.add_field(
            name="Python",
            value=sys.version,
            inline=False,
        )

        return embed

    # def embed_installed_packages(self) -> discord.Embed:
    #     """
    #     == Installed packages ==
    #     py-cord
    #     ...
    #     """

    #     embed = discord.Embed(
    #         color=0xFF24CF,
    #         title=f"已安裝的套件",
    #     )

    #     embed.add_field(
    #         name="package_name".lower,
    #         value="package_version",
    #         inline=True,
    #     )

    #     return embed

    def embed_version_info_footer(self) -> discord.Embed:
        """
        Main footer of the version information embeds.
        """

        return discord.Embed(
            color=0xFF24CF,
            footer=discord.EmbedFooter(
                text=datetime.datetime.now(tz=datetime.timezone.utc).strftime(
                    format="%Y-%m-%d %H:%M:%S (UTC)"
                )
            ),
        )

    @discord.slash_command(name="version_info", description="版本資訊")
    async def version_info(self, interaction) -> None:
        interaction = cast(discord.Interaction, interaction)

        assert (
            interaction.user
        ), "Interaction may be in PING interactions, so that interaction.user is invalid."
        assert interaction.channel, "There are no channel returned from interation."

        await interaction.response.send_message(embeds=self.embeds_version_info())


def setup(bot: discord.Bot):
    bot.add_cog(VersionInfo(bot))
