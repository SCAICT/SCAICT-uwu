# Third-party imports
import discord
from discord.ext import commands
# Local imports
from build.build import Build
from cog.core.sql import link_sql
from cog.core.sql import read
from cog.core.sql import write
from cog.core.sql import end

class AdminRole(Build):
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(self.Gift())

    # 成員身分組
    class RoleView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout = None) # timeout of the view must be set to None

        @discord.ui.button(
            label = "領取身分組",
            style = discord.ButtonStyle.blurple,
            emoji = "🥇",
            custom_id = "take_the_role"
        )
        # pylint: disable-next = unused-argument
        async def button_callback_1(self, button, interaction):
            role = discord.utils.get(interaction.guild.roles, name = "ADMIN")
            await interaction.user.add_roles(role)
            await interaction.response.send_message("已領取身分組 `ヾ(≧▽≦*)o`", ephemeral = True)

    @discord.slash_command()
    async def create_role_button(self, ctx):
        if ctx.author.guild_permissions.administrator:
            embed = discord.Embed(color = 0x16b0fe)
            # pylint: disable-next = line-too-long
            embed.set_thumbnail(url = "https://emojiisland.com/cdn/shop/products/Nerd_with_Glasses_Emoji_2a8485bc-f136-4156-9af6-297d8522d8d1_large.png?v=1571606036")
            embed.add_field(name = "哈囉 點一下", value = "  ", inline = False)
            await ctx.respond(embed = embed, view = self.RoleView())
                # 禮物按鈕
    class Gift(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)  # timeout of the view must be set to None
            self.type=None#存放這個按鈕是送電電點還是抽獎卷
            self.count=0#存放這個按鈕是送多少電電點/抽獎卷
        #發送獎勵
        @staticmethod
        def __reward(uid,userName,type,bouns):
            CONNECT, CURSOR = link_sql()
            nowPoint=read(uid,type, CURSOR)
            write(uid, type, nowPoint+bouns, CURSOR)
            end(CONNECT, CURSOR)
            print(f"{uid} {userName} get {bouns} {type} by Gift")
        #點擊後會觸發的動作
        @discord.ui.button(label="領取獎勵", 
                           style=discord.ButtonStyle.success,
                           custom_id="get_gift")
        async def get_gift(self, button: discord.ui.Button,ctx):
            self.type="point" if self.type=="電電點" else "ticket"
            self.__reward(ctx.user.id, ctx.user,self.type,self.count)
            #LOG
            button.label = "已領取" # change the button's label to "已領取"
            button.disabled = True  # 關閉按鈕，避免重複點擊
            await ctx.response.edit_message(view=self)
      
    @discord.slash_command(name="發送禮物",description="dm_gift")
    async def senddm(self, ctx,
                     target:discord.Option(str, "發送對象", required=True),
                     type:discord.Option(str, "送禮內容",choices=["電電點", "抽獎卷"]),
                    # dm gift
                    count:discord.Option(int,"數量")):
        if ctx.author.guild_permissions.administrator:
            #不能發送負數
            if count<=0:
                await ctx.respond("不能發送 0 以下個禮物！",ephemeral=True)
                return
            manager=ctx.author
            target = await self.bot.fetch_user(target)
            #管理者介面提示
            await ctx.respond(f"{manager} 已發送 {count} {type} 給 {target}")
            #生成按鈕物件
            view = self.Gift()
            view.type=type
            view.count=count
            embed = discord.Embed(title=f"你收到了 {count} {type}！", description=":gift:", color=discord.Color.blurple())
            # dm 一個 Embed 和領取按鈕
            await target.send(embed=embed)
            await target.send(view=view)
        else:
            await ctx.respond("你沒有權限使用這個指令！",ephemeral=True)
            return
def setup(bot):
    bot.add_cog(AdminRole(bot))
