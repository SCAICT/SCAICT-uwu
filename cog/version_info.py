# Standard imports
import datetime

# import subprocess
import sys
from typing import cast

# Third-party imports
import discord
from discord.ext import commands


class VersionInfo(commands.Cog):
    _SCAICT_UWU_VERSION_NUMBER: str = "0.1.13.dev0"
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

    _SCAICT_UWU_IMAGE = (
        "https://github.com/SCAICT/SCAICT-uwu/blob/851186b/uwu.png?raw=true"
    )
    """
    Current hardcoded workaround
    """

    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    def _embed_version_info(self) -> discord.Embed:
        """
        The version information embed.
        """

        # TODO: Git hash
        # process = subprocess.Popen(
        #     ['git', 'rev-parse', 'HEAD'],
        #     shell=False,
        #     stdout=subprocess.PIPE
        # )
        # git_head_hash = process.communicate()[0].strip()

        # == Installed software ==
        #
        # '''scaict_uwu'''
        # version_num (git_hash_to-do)
        # date
        #
        # '''python'''
        # version
        #
        # '''pip''' <!-- To-do -->
        # version
        #
        # '''mysql''' <!-- To-do -->
        # version
        #
        # == Installed packages == <!-- To-do -->
        description = (
            "### 已安裝的軟體\n\n"
            + "**中電喵**\n"
            + self._SCAICT_UWU_VERSION
            + "\n\n"
            + "**Python**\n"
            + sys.version
            # + "\n\n"
            # + "### 已安裝的套件"
        )

        return discord.Embed(
            color=0xFF24CF,
            title="版本資訊",
            description=description,
            fields=self._embed_fields_installed_packages(),
            author=discord.EmbedAuthor(
                name="中電喵",
                icon_url=self.bot.user.display_avatar.url,
            ),
            thumbnail=self._SCAICT_UWU_IMAGE,
            footer=discord.EmbedFooter(
                text=datetime.datetime.now(tz=datetime.timezone.utc).strftime(
                    format="%Y-%m-%d %H:%M:%S (UTC)"
                )
            ),
        )

    def _embed_fields_installed_packages(self) -> list[discord.EmbedField] | None:
        """
        flask: version,   mysql-connector-python: version,
        py-cord: version, ...
        """

        # fields = []

        # TODO:
        # fields.append(
        #     discord.EmbedField(
        #         name="package_name".lower,
        #         value="package_version",
        #         inline=True,
        #     )
        # )

        # return fields
        return None

    @discord.slash_command(name="version_info", description="版本資訊")
    async def version_info(self, interaction) -> None:
        interaction = cast(discord.Interaction, interaction)

        assert (
            interaction.user
        ), "Interaction may be in PING interactions, so that interaction.user is invalid."
        assert interaction.channel, "There are no channel returned from interation."

        await interaction.response.send_message(embed=self._embed_version_info())


def setup(bot: discord.Bot):
    bot.add_cog(VersionInfo(bot))
