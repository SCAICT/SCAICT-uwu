"""
電電點數位特權。

用電電點兌換不需要物流的數位商品：
/custom_role 租借自訂身分組（可自訂名稱與顏色，到期自動回收）、
/chat_nick 設定中電喵對你的專屬稱呼。
價格與租期設定在 database/server.config.json 的 perk 區塊。
"""

# Future statements
from __future__ import annotations

# Standard imports
import datetime
import json
import os
import re

# Third-party imports
import discord
import discord.ext.commands
import discord.ext.tasks

# Local imports
import cog.core.sql


def get_perk_config() -> dict:
    """
    讀取 server.config.json 中的 perk 設定。

    Returns:
        dict:
            perk 設定，讀取失敗時為空 dict（使用程式內預設值）。
    """

    try:
        with open(
            f"{os.getcwd()}/database/server.config.json", "r", encoding="utf-8"
        ) as config_file:
            return json.load(config_file)["SCAICT-alpha"].get("perk", {})
    except FileNotFoundError:
        print("Configuration file not found.")
    except json.JSONDecodeError:
        print("Error decoding JSON.")
    except KeyError as exception:
        print(f"Key error in configuration file: {exception}")

    return {}


PERK_CONFIG = get_perk_config()
ROLE_PRICE = PERK_CONFIG.get("customRolePrice", 500)
ROLE_DAYS = PERK_CONFIG.get("customRoleDays", 30)
NICK_PRICE = PERK_CONFIG.get("chatNickPrice", 200)

# 不允許出現在身分組名稱或稱呼中的敏感詞彙
# （會長名字、違反善良風俗的詞等），由 server.config.json 的 perk.forbidden 維護
FORBIDDEN_WORDS = [word for word in PERK_CONFIG.get("forbidden", []) if word]

ROLE_NAME_MAX_LENGTH = 32
NICK_MAX_LENGTH = 20

# 預設顏色（也接受六位十六進位色碼）
COLOR_PRESETS = {
    "紅色": "ED4245",
    "橙色": "E67E22",
    "黃色": "FEE75C",
    "綠色": "57F287",
    "青色": "1ABC9C",
    "藍色": "3498DB",
    "紫色": "9B59B6",
    "粉紅色": "EB459E",
    "金色": "F1C40F",
    "白色": "FFFFFF",
    "灰色": "95A5A6",
    "黑色": "23272A",
}


def parse_colour(color: str) -> discord.Colour | None:
    """
    將預設顏色名稱或十六進位色碼轉成 discord.Colour。

    Parameters:
        color (str):
            預設顏色名稱（如「粉紅色」）或六位色碼（如 F5A9B8）。

    Returns:
        discord.Colour | None:
            解析失敗時為 None。
    """

    color = color.strip().lstrip("#")
    color = COLOR_PRESETS.get(color, color)

    if re.fullmatch("[0-9A-Fa-f]{6}", color):
        return discord.Colour(int(color, 16))

    return None


async def color_autocomplete(ctx: discord.AutocompleteContext) -> list[str]:
    """
    顏色選項的自動完成：輸入時列出符合的預設顏色。

    Parameters:
        ctx (discord.AutocompleteContext):
            自動完成的上下文。

    Returns:
        list[str]:
            建議的顏色名稱。
    """

    value = (ctx.value or "").strip()
    matches = [name for name in COLOR_PRESETS if value in name]

    return matches or list(COLOR_PRESETS)


def sanitize(text: str) -> str:
    """
    移除會影響 SQL 寫入與訊息排版的字元。

    Parameters:
        text (str):
            原始輸入。

    Returns:
        str:
            清理後的文字。
    """

    return re.sub(r'["\\\n\r`]', "", text).strip()


def contains_forbidden(text: str) -> bool:
    """
    判斷文字是否包含任何敏感詞彙（FORBIDDEN_WORDS）。

    Parameters:
        text (str):
            要檢查的文字。

    Returns:
        bool:
            包含敏感詞彙時為 True。
    """

    lowered = text.lower()

    return any(word.lower() in lowered for word in FORBIDDEN_WORDS)


def is_same_as_member(guild: discord.Guild | None, user_id: int, text: str) -> bool:
    """
    判斷文字是否與其他成員的顯示名稱完全相同（防撞名）。

    Parameters:
        guild (discord.Guild | None):
            所在的伺服器，無法取得時回傳 False。
        user_id (int):
            提出請求的使用者 ID，自己的名稱不算撞名。
        text (str):
            要檢查的文字。

    Returns:
        bool:
            與其他成員名稱完全相同時為 True。
    """

    if guild is None:
        return False

    lowered = text.lower()

    for member in guild.members:
        if member.id == user_id:
            continue

        if member.display_name.lower() == lowered:
            return True

    return False


class Perk(discord.ext.commands.Cog):
    """
    電電點數位特權：自訂身分組與中電喵專屬稱呼。

    Attributes:
        bot (discord.Bot):
            掛載這個 cog 的 bot。
    """

    bot: discord.Bot

    def __init__(self, bot):
        self.bot = bot
        self.expire_check.start()

    def cog_unload(self):
        self.expire_check.cancel()

    @discord.slash_command(
        name="custom_role",
        description=f"用 {ROLE_PRICE} 電電點租借自訂身分組 {ROLE_DAYS} 天",
    )
    async def custom_role(
        self,
        ctx,
        name: str = discord.Option(str, "身分組名稱"),
        color: str = discord.Option(
            str,
            "顏色：選預設顏色或輸入六位色碼（例如 F5A9B8）",
            autocomplete=color_autocomplete,
            default="",
        ),
    ) -> None:
        """
        Parameters:
            ctx:
            name (str):
            color (str):
        """

        if ctx.guild is None:
            await ctx.respond("這個指令只能在伺服器內使用！", ephemeral=True)

            return

        name = sanitize(name)

        if not 1 <= len(name) <= ROLE_NAME_MAX_LENGTH:
            await ctx.respond(
                f"身分組名稱長度需在 1~{ROLE_NAME_MAX_LENGTH} 字元之間！",
                ephemeral=True,
            )

            return

        if contains_forbidden(name):
            await ctx.respond("這個身分組名稱包含了不允許使用的詞彙！", ephemeral=True)

            return

        if is_same_as_member(ctx.guild, ctx.author.id, name):
            await ctx.respond(
                "這個身分組名稱與其他成員的名字相同，請換一個！", ephemeral=True
            )

            return

        colour = None

        if color:
            colour = parse_colour(color)

            if colour is None:
                await ctx.respond(
                    "看不懂這個顏色！可以選預設顏色："
                    f"{'、'.join(COLOR_PRESETS)}，"
                    "或輸入六位十六進位色碼（例如 F5A9B8）",
                    ephemeral=True,
                )

                return

        # 先告知 Discord 稍等，避免資料庫或 API 較慢時超過 3 秒限制
        await ctx.defer()

        user_id = ctx.author.id
        connection, cursor = cog.core.sql.link_sql()
        point = cog.core.sql.read(user_id, "point", cursor)

        if point < ROLE_PRICE:
            await ctx.respond(
                f"電電點不足！需要 {ROLE_PRICE} 點，你目前只有 {point} 點。"
            )
            cog.core.sql.end(connection, cursor)

            return

        # 已有租借中的身分組就改名續租，否則建立新的
        role_id = cog.core.sql.read(user_id, "role_id", cursor, table="custom_role")
        role = ctx.guild.get_role(role_id) if role_id else None

        try:
            if role is None:
                role = await ctx.guild.create_role(
                    name=name,
                    colour=colour or discord.Colour.default(),
                    reason="電電點租借自訂身分組",
                )
            elif colour is None:
                # 沒指定色碼就只改名，保留原本的顏色
                await role.edit(name=name)
            else:
                await role.edit(name=name, colour=colour)

            # 優先度最高：移到身分組清單最上方。
            # Discord 限制角色不能高於 bot 自己的 top role，
            # 所以取 bot 最高可設定的位置（top role 下面一格）
            try:
                highest_position = max(ctx.guild.me.top_role.position - 1, 0)
                await role.edit(position=highest_position)
            except discord.HTTPException as exception:
                # 移動位置失敗不影響租借，記錄即可
                print(f"Failed to move role to top: {exception}")

            await ctx.author.add_roles(role)
        except discord.Forbidden:
            await ctx.respond("我沒有管理身分組的權限，請聯絡管理員！")
            cog.core.sql.end(connection, cursor)

            return

        # 續租從原到期日往後算，新租從現在起算
        now = datetime.datetime.now()
        old_expire = cog.core.sql.read(
            user_id, "role_expire", cursor, table="custom_role"
        )
        base = old_expire if old_expire is not None and old_expire > now else now
        new_expire = base + datetime.timedelta(days=ROLE_DAYS)

        cog.core.sql.write(user_id, "point", point - ROLE_PRICE, cursor)
        cog.core.sql.write(user_id, "role_id", role.id, cursor, table="custom_role")
        cog.core.sql.write(
            user_id,
            "role_expire",
            new_expire.strftime("%Y-%m-%d %H:%M:%S"),
            cursor,
            table="custom_role",
        )
        cog.core.sql.end(connection, cursor)
        print(
            f"{user_id}, {ctx.author} rent custom role {role.id} {datetime.datetime.now()}"
        )

        # 沒指定顏色時沿用身分組現有的顏色，沒有顏色就用預設綠色
        embed_colour = colour or (
            role.colour if role.colour.value else discord.Colour(0x14E15C)
        )
        embed = discord.Embed(color=embed_colour)
        embed.add_field(name="租借成功！", value=role.mention, inline=False)
        embed.add_field(
            name="到期日",
            value=new_expire.strftime("%Y-%m-%d %H:%M"),
            inline=False,
        )
        embed.set_footer(text=f"已扣除 {ROLE_PRICE} 電電點，到期後自動回收")
        await ctx.respond(embed=embed)

    @discord.slash_command(
        name="chat_nick",
        description=f"用 {NICK_PRICE} 電電點設定中電喵對你的稱呼",
    )
    async def chat_nick(
        self, ctx, nickname: str = discord.Option(str, "想被叫的稱呼")
    ) -> None:
        """
        Parameters:
            ctx:
            nickname (str):
        """

        nickname = sanitize(nickname)

        if not 1 <= len(nickname) <= NICK_MAX_LENGTH:
            await ctx.respond(
                f"稱呼長度需在 1~{NICK_MAX_LENGTH} 字元之間！", ephemeral=True
            )

            return

        if contains_forbidden(nickname):
            await ctx.respond("這個稱呼包含了不允許使用的詞彙！", ephemeral=True)

            return

        if is_same_as_member(ctx.guild, ctx.author.id, nickname):
            await ctx.respond(
                "這個稱呼與其他成員的名字相同，請換一個！", ephemeral=True
            )

            return

        # 先告知 Discord 稍等，避免資料庫較慢時超過 3 秒限制
        await ctx.defer()

        user_id = ctx.author.id
        connection, cursor = cog.core.sql.link_sql()
        point = cog.core.sql.read(user_id, "point", cursor)

        if point < NICK_PRICE:
            await ctx.respond(
                f"電電點不足！需要 {NICK_PRICE} 點，你目前只有 {point} 點。"
            )
            cog.core.sql.end(connection, cursor)

            return

        cog.core.sql.write(user_id, "point", point - NICK_PRICE, cursor)
        cog.core.sql.write(user_id, "nickname", nickname, cursor, table="chat_nick")
        cog.core.sql.end(connection, cursor)
        print(f"{user_id}, {ctx.author} set chat nick {datetime.datetime.now()}")

        embed = discord.Embed(color=0x14E15C)
        embed.add_field(
            name="設定成功！", value=f"中電喵之後會叫你「{nickname}」喵", inline=False
        )
        embed.set_footer(text=f"已扣除 {NICK_PRICE} 電電點，重新購買即可更改")
        await ctx.respond(embed=embed)

    @discord.ext.tasks.loop(minutes=30)
    async def expire_check(self) -> None:
        """
        回收過期的自訂身分組。
        """

        try:
            connection, cursor = cog.core.sql.link_sql()
            cursor.execute(
                "SELECT uid, role_id FROM custom_role"
                " WHERE role_expire IS NOT NULL AND role_expire < %s",
                (datetime.datetime.now(),),
            )
            expired = cursor.fetchall()

            for user_id, role_id in expired:
                role = None

                for guild in self.bot.guilds:
                    role = guild.get_role(role_id)

                    if role is not None:
                        break

                if role is not None:
                    try:
                        await role.delete(reason="自訂身分組租期已到")
                    except discord.Forbidden:
                        print(f"No permission to delete role {role_id}")

                        continue

                cursor.execute("DELETE FROM custom_role WHERE uid = %s", (user_id,))
                print(
                    f"{user_id} custom role {role_id} expired {datetime.datetime.now()}"
                )

            cog.core.sql.end(connection, cursor)
        # pylint: disable-next = broad-exception-caught
        except Exception as exception:
            print(f"Error in expire_check: {exception}")

    @expire_check.before_loop
    async def before_expire_check(self) -> None:
        await self.bot.wait_until_ready()


def setup(bot: discord.Bot) -> None:
    """
    Parameters:
        bot (discord.Bot):
    """

    bot.add_cog(Perk(bot))
