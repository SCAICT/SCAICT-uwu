# Standard imports
import asyncio
import json
import os
from random import choice

# Third-party imports
import discord

# Local imports
from cog.core.sql import link_sql
from cog.core.sql import end


def open_json():
    # open configuration file
    os.chdir("./")
    with open(
        f"{os.getcwd()}/DataBase/server.config.json", "r", encoding="utf-8"
    ) as file:
        global_settings = json.load(file)
    return global_settings


def get_total_points():
    connection, cursor = link_sql()
    cursor.execute("SELECT SUM(point) FROM `user`")
    points = cursor.fetchone()[0]
    end(connection, cursor)
    return points


async def update_channel(bot):
    channel = open_json()["SCAICT-alpha"]["channel"]
    await bot.wait_until_ready()
    guild = bot.get_guild(channel["serverID"])  # YOUR_GUILD_ID

    if guild is None:
        print("找不到指定的伺服器")
        return

    member_channel = guild.get_channel(channel["memberCount"])  # YOUR_CHANNEL_ID
    point_channel = guild.get_channel(channel["pointCount"])
    if channel is None:
        print("找不到指定的頻道")
        return
    prev_points = get_total_points()
    prev_total_members = guild.member_count
    while not bot.is_closed():
        points = get_total_points()
        total_members = guild.member_count
        if points != prev_points:
            await point_channel.edit(name=f"🔋總電量：{points}")
            prev_points = points
        if total_members != prev_total_members:
            await member_channel.edit(name=f"👥電池數：{total_members}")
            prev_total_members = total_members
        await asyncio.sleep(600)


async def change_status(bot):
    await bot.wait_until_ready()
    announcements = [
        "SCAICT.org",
        "今天 /charge 了嗎？",
        "要不要一起猜顏色",
        "要不要一起猜拳？",
        "debug",
    ]
    while not bot.is_closed():
        status = choice(announcements)
        await bot.change_presence(activity=discord.Game(name=status))
        await asyncio.sleep(10)
