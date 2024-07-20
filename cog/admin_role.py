# Third-party imports
import discord
from discord.ext import commands

# Local imports
from build.build import Build
from cog.core.sql import link_sql, read, write, end

class AdminRole(Build):
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.bot.add_view(self.Gift())

    # 成員身分組
    class RoleView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)  # timeout of the view must be set to None

        @discord.ui.button(
            label="領取身分組",
            style=discord.ButtonStyle.blurple,
            emoji="🥇",
            custom_id="take_the_role"
        )
        async def button_callback_1(self, button, interaction) -> None:
            role = discord.utils.get(interaction.guild.roles, name="ADMIN")
            await interaction.user.add_roles(role)
            await interaction.response.send_message("已領取身分組 `ヾ(≧▽≦*)o`", ephemeral=True)

    @discord.slash_command()
    async def create_role_button(self, ctx) -> None:
        if ctx.author.guild_permissions.administrator:
            embed = discord.Embed(color=0x16b0fe)
            embed.set_thumbnail(url="https://emojiisland.com/cdn/shop/products/Nerd_with_Glasses_Emoji_2a8485bc-f136-4156-9af6-297d8522d8d1_large.png?v=1571606036")
            embed.add_field(name="哈囉 點一下", value="  ", inline=False)
            await ctx.respond(embed=embed, view=self.RoleView())

    # 禮物按鈕
    class Gift(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)  # timeout of the view must be set to None
            self.type = None  # 存放這個按鈕是送電電點還是抽獎卷，預設 None ，在創建按鈕時會設定 see view.type = gift_type
            self.count = 0  # 存放這個按鈕是送多少電電點/抽獎卷

        # 發送獎勵
        @staticmethod
        def __reward(uid, user_name, bonus_type, bonus):
            connection, cursor = link_sql()
            current_point = read(uid, bonus_type, cursor)
            write(uid, bonus_type, current_point + bonus, cursor)
            end(connection, cursor)
            print(f"{uid} {user_name} get {bonus} {bonus_type} by Gift")

        # 存資料庫存取按鈕屬性(包括獎勵類型、數量)
        def __read_db(self, btn_id):
            connection, cursor = link_sql()
            cursor.execute(f"SELECT type, count FROM `gift` WHERE `btnID`={btn_id}")
            ret = cursor.fetchall()
            cursor.execute(f"DELETE FROM `gift` WHERE `btnID`={btn_id}")
            end(connection, cursor)
            return ret[0][0], ret[0][1]  # type, count

        # 點擊後會觸發的動作
        @discord.ui.button(
            label="領取獎勵",
            style=discord.ButtonStyle.success,
            custom_id="get_gift"
        )
        async def get_gift(self, button: discord.ui.Button, ctx) -> None:
            self.type, self.count = self.__read_db(ctx.message.id)  # 傳入按鈕的訊息 ID
            self.type = "point" if self.type == "電電點" else "ticket"
            self.__reward(ctx.user.id, ctx.user, self.type, self.count)
            # log
            button.label = "已領取"  # change the button's label to "已領取"
            button.disabled = True  # 關閉按鈕，避免重複點擊
            await ctx.response.edit_message(view=self)

    @discord.slash_command(name="發送禮物", description="dm_gift")
    async def send_dm_gift(
        self,
        ctx,
        target_str: discord.Option(str, "發送對象（用半形逗號分隔多個使用者名稱）", required=True),
        gift_type: discord.Option(str, "送禮內容", choices=["電電點", "抽獎券"]),
        count: discord.Option(int, "數量")
    ) -> None:
        if ctx.author.guild_permissions.administrator:
            await ctx.defer()  # 確保機器人請求不會超時
            # 不能發送負數
            if count <= 0:
                await ctx.respond("不能發送 0 以下個禮物！", ephemeral=True)
                return
            manager = ctx.author
            target_usernames = target_str.split(',')
            target_users = []

            async def fetch_user_by_name(name):
                user_obj = discord.utils.find(lambda u: u.name == name, self.bot.users)
                if user_obj:
                    return await self.bot.fetch_user(user_obj.id)

            for username in target_usernames:
                username = username.strip()
                try:
                    user = await fetch_user_by_name(username)
                    target_users.append(user)
                except (ValueError, Exception) as e:
                    await ctx.respond(f"找不到使用者 ： {username}{e}", ephemeral=True)
                    return

            # 管理者介面提示
            await ctx.respond(f"{manager} 已發送 {count} {gift_type} 給 {', '.join([user.name for user in target_users])}")
            # 產生按鈕物件
            view = self.Gift()
            view.type = gift_type
            view.count = count
            embed = discord.Embed(
                title=f"你收到了 {count} {gift_type}！",
                description=":gift:",
                color=discord.Color.blurple()
            )

            async def record_db(btn_id, gift_type, count, recipient):
                connection, cursor = link_sql()
                cursor.execute("INSERT INTO `gift`(`btnID`, `type`, `count`, `recipient`) VALUES (%s, %s, %s, %s)", (btn_id, gift_type, count, recipient))
                end(connection, cursor)

            # DM 一個 Embed 和領取按鈕
            for target_user in target_users:
                try:
                    await target_user.send(embed=embed)
                    msg = await target_user.send(view=view)
                    await record_db(msg.id, gift_type, count, target_user.name)
                except discord.Forbidden:
                    await ctx.respond(f"無法向使用者 {target_user.name} 傳送訊息，可能是因為他們關閉了 DM。", ephemeral=True)
        else:
            await ctx.respond("你沒有權限使用這個指令！", ephemeral=True)
            return

def setup(bot):
    bot.add_cog(AdminRole(bot))
