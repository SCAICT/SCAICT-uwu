# Future statements
from __future__ import annotations

# Standard imports
import json
import os
import random
import typing

# Third-party imports
import discord
import discord.ext.commands

# Local imports
import cog.core.sql


def get_channels() -> typing.Any | dict:
    """
    取得特殊用途頻道的列表，這裡會用來判斷是否在簽到頻道簽到，否則不予受理

    Returns:
        typing.Any | dict:
    """

    try:
        with open(
            f"{os.getcwd()}/DataBase/server.config.json", "r", encoding="utf-8"
        ) as file:
            return json.load(file)["SCAICT-alpha"]
    except FileNotFoundError:
        print("Configuration file not found.")

        return {}
    except json.JSONDecodeError:
        print("Error decoding JSON.")

        return {}


stickers = get_channels()["stickers"]["zap"]


class Game(discord.ext.commands.Cog):
    # User can use this command to play ✊-🤚-✌️ with the bot in the command channel
    @discord.slash_command(name="rock_paper_scissors", description="玩剪刀石頭布")
    # user can choose ✊, 🤚, or ✌️ in their command
    async def rock_paper_scissors(
        self,
        interaction: discord.Interaction,
        choice: str = discord.Option(str, choices=["✊", "🤚", "✌️"]),
    ) -> None:
        """
        Parameters:
            interaction (discord.Interaction):
            choice (str):
        """

        if interaction.channel.id != get_channels()["channel"]["commandChannel"]:
            await interaction.response.send_message("這裡不是指令區喔", ephemeral=True)

            return

        user_id = interaction.user.id
        user_display_name = interaction.user

        try:
            connection, cursor = cog.core.sql.link_sql()  # SQL 會話

            point = cog.core.sql.read(user_id, "point", cursor)

            if point < 5:
                await interaction.response.send_message(
                    "你的電電點不足以玩這個遊戲", ephemeral=True
                )
                cog.core.sql.end(connection, cursor)

                return

            if choice not in ["✊", "🤚", "✌️"]:
                await interaction.response.send_message(
                    "請輸入正確的選擇", ephemeral=True
                )
                cog.core.sql.end(connection, cursor)

                return

            bot_choice = random.choice(["✊", "🤚", "✌️"])
            game_outcomes = {
                ("✌️", "✊"): 5,
                ("✌️", "🤚"): -5,
                ("✊", "✌️"): -5,
                ("✊", "🤚"): 5,
                ("🤚", "✌️"): 5,
                ("🤚", "✊"): -5,
            }

            if bot_choice == choice:
                await interaction.response.send_message(
                    content=f"我出{bot_choice}，平手。你還有{point}{stickers}"
                )
            else:
                point += game_outcomes[(bot_choice, choice)]
                result = (
                    "你贏了" if game_outcomes[(bot_choice, choice)] > 0 else "你輸了"
                )
                await interaction.response.send_message(
                    content=f"我出{bot_choice}，{result}，你還有{point}{stickers}"
                )
                # pylint: disable-next = line-too-long
                print(
                    f"{user_id}, {user_display_name} Get {game_outcomes[(bot_choice, choice)]} point by playing rock-paper-scissors"
                )
            cog.core.sql.write(user_id, "point", point, cursor)
        # pylint: disable-next = broad-exception-caught
        except Exception as exception:
            print(f"Error: {exception}")

        cog.core.sql.end(connection, cursor)

    @discord.slash_command(name="number_status", description="數數狀態")
    async def number_status(self, interaction: discord.Interaction) -> None:
        """
        Parameters:
            interaction (discord.Interaction):
        """

        try:
            connection, cursor = cog.core.sql.link_sql()  # SQL 會話
            cursor.execute("SELECT seq FROM game")
            current_sequence = cursor.fetchone()[0]
        # pylint: disable-next = broad-exception-caught
        except Exception as exception:
            print(f"Error: {exception}")

        cog.core.sql.end(connection, cursor)
        embed = discord.Embed(
            title="現在數到",
            description=f"{current_sequence} (dec) 了，接下去吧!",
            color=0xFF24CF,
        )
        await interaction.response.send_message(embed=embed)


def setup(bot: discord.Bot) -> None:
    """
    Parameters:
        bot (discord.Bot):
    """

    bot.add_cog(Game(bot))
