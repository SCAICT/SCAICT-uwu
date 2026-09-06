"""
中電喵 AI 聊天功能。

在訊息中 @中電喵 即可與她聊天，不需要使用任何指令。
底層串接 Google Gemini API（有免費額度），並以省 token 為原則設計：
回覆長度上限、對話歷史長度上限、使用者冷卻時間。
"""

# Future statements
from __future__ import annotations

# Standard imports
import collections
import os
import re
import time

# Third-party imports
import discord.ext.commands
import dotenv
import google.genai
import google.genai.errors
import google.genai.types
import openai

# Local imports
import cog.core.sql

dotenv.load_dotenv(f"{os.getcwd()}/.env")

# 免費額度內每日請求數最多、付費也最便宜的模型
# 額度與定價見 https://ai.google.dev/pricing
CHAT_MODEL = os.getenv("CHAT_MODEL", "gemini-2.5-flash-lite")
# 主模型壅塞（503）時的備援模型
FALLBACK_MODEL = os.getenv("CHAT_FALLBACK_MODEL", "gemini-2.5-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 第三層備援：Groq 的免費額度與 Google 完全獨立，
# 未設定 GROQ_API_KEY 時自動停用這一層
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# 為了省 token 所做的限制
MAX_REPLY_TOKENS = 1000  # 單次回覆的輸出 token 上限
MAX_INPUT_CHARS = 500  # 單則使用者訊息的長度上限（字元）
HISTORY_LIMIT = 10  # 每個頻道保留的對話歷史則數
COOLDOWN_SECONDS = 5  # 同一位使用者兩次對話間的冷卻秒數


def load_knowledge() -> str:
    """
    讀取中電喵的固定知識（database/chat_knowledge.txt）。

    內容會附加在 system prompt 裡，讓她能正確回答
    關於中電會與伺服器功能的問題；檔案不存在時略過。

    Returns:
        str:
            知識內容，讀取失敗時為空字串。
    """

    try:
        with open(
            f"{os.getcwd()}/database/chat_knowledge.txt", "r", encoding="utf-8"
        ) as knowledge_file:
            return knowledge_file.read().strip()
    except FileNotFoundError:
        print("chat_knowledge.txt not found; chat runs without fixed knowledge.")
    except OSError as exception:
        print(f"Error reading chat_knowledge.txt: {exception}")

    return ""


KNOWLEDGE = load_knowledge()

SYSTEM_PROMPT = (
    "你是中電喵，一隻住在 SCAICT 中電會 Discord 伺服器的貓咪。"
    "請用繁體中文、友善可愛的語氣回覆，偶爾在句尾加「喵」。"
    "回覆要簡短，盡量三句以內，不要超過 1500 字元。"
    "訊息開頭的「名字：」是發言者的名字，回覆時不要模仿這個格式。"
)

if KNOWLEDGE:
    SYSTEM_PROMPT += "\n\n以下是你知道的事實，回答相關問題時以此為準：\n" + KNOWLEDGE

GENERATE_CONFIG = google.genai.types.GenerateContentConfig(
    system_instruction=SYSTEM_PROMPT,
    max_output_tokens=MAX_REPLY_TOKENS,
    # 關閉 thinking 以節省 token（flash 系列適用；
    # 若改用 gemini-2.5-pro 需移除這行）
    thinking_config=google.genai.types.ThinkingConfig(thinking_budget=0),
)


class Chat(discord.ext.commands.Cog):
    """
    @中電喵 聊天功能。

    Attributes:
        bot (discord.Bot):
            掛載這個 cog 的 bot。
        client (google.genai.Client):
            Gemini API 客戶端，未設定 GEMINI_API_KEY 時為 None。
        history (collections.defaultdict):
            頻道 ID 對應到該頻道的對話歷史。
        last_used (dict):
            使用者 ID 對應到上次對話的時間戳。
    """

    bot: discord.Bot

    client: google.genai.Client

    groq: openai.AsyncOpenAI | None

    history: collections.defaultdict

    last_used: dict

    def __init__(self, bot):
        self.bot = bot
        self.client = (
            google.genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
        )
        self.groq = (
            openai.AsyncOpenAI(base_url=GROQ_BASE_URL, api_key=GROQ_API_KEY)
            if GROQ_API_KEY
            else None
        )
        # 每個頻道各自保留一小段對話歷史，超過上限自動丟棄最舊的
        self.history = collections.defaultdict(
            lambda: collections.deque(maxlen=HISTORY_LIMIT)
        )
        self.last_used = {}

    @discord.ext.commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """
        Parameter:
            message (discord.Message):
        """

        # 機器人發言不可當成觸發條件，必須排除
        if message.author.bot:
            return

        if not self.is_mentioned(message):
            return

        if self.client is None:
            await message.reply(
                "還沒設定 GEMINI_API_KEY，沒辦法聊天喵……", mention_author=False
            )

            return

        # 冷卻中告知使用者稍等（訊息幾秒後自動刪除，避免洗頻），
        # 不呼叫 API 以免燒掉免費額度
        now = time.monotonic()
        last = self.last_used.get(message.author.id, 0)

        if now - last < COOLDOWN_SECONDS:
            remain = int(COOLDOWN_SECONDS - (now - last)) + 1
            await message.reply(
                f"太快了喵！等 {remain} 秒再叫我一次～",
                mention_author=False,
                delete_after=5,
            )

            return

        self.last_used[message.author.id] = now

        content = self.clean_content(message)

        if not content:
            # 只有 @ 沒有內容就不呼叫 API，直接打招呼
            await message.reply("找我有什麼事嗎喵？", mention_author=False)

            return

        await self.chat(message, content)

    def is_mentioned(self, message: discord.Message) -> bool:
        """
        判斷訊息是否提及中電喵（機器人本身，或她的同名身分組）。

        輸入 @uwu 時，選單常會選到機器人的專屬身分組而不是
        機器人本人，兩種在畫面上幾乎一樣，因此都要視為觸發。

        Parameters:
            message (discord.Message):
                觸發的訊息。

        Returns:
            bool:
                有提及時為 True。
        """

        if self.bot.user in message.mentions:
            return True

        if message.guild is not None and message.role_mentions:
            bot_member = message.guild.me

            return any(role in bot_member.roles for role in message.role_mentions)

        return False

    @staticmethod
    def sanitize_mentions(text: str) -> str:
        """
        破壞回覆中可能被 Discord 解析成提及的字串，防止誘導 @everyone。

        在字元之間插入零寬空格，讓 Discord 無法解析成 @everyone / @here，
        也不會顯示成可點擊的藍色提及。內嵌的使用者 / 身分組 ID 則直接移除。

        Parameters:
            text (str):
                AI 產生的回覆內容。

        Returns:
            str:
                清除提及解析後的內容。
        """

        # 把 @everyone / @here 中間插入零寬空格（U+200B）
        for keyword in ("everyone", "here"):
            text = text.replace(f"@{keyword}", f"@\u200b{keyword}")

        # 移除 <@123> / <@!123> / <@&456> 這類提及語法
        text = re.sub(r"<@!?\d+>", "", text)
        text = re.sub(r"<@&\d+>", "", text)

        return text

    def clean_content(self, message: discord.Message) -> str:
        """
        移除訊息中的機器人提及並截斷過長的內容。

        Parameters:
            message (discord.Message):
                觸發的訊息。

        Returns:
            str:
                清理後的訊息內容。
        """

        content = message.content
        mentions = [f"<@{self.bot.user.id}>", f"<@!{self.bot.user.id}>"]

        if message.guild is not None:
            # 也清掉機器人身分組的提及（@uwu 選到身分組的情況）
            mentions += [f"<@&{role.id}>" for role in message.guild.me.roles]

        for mention in mentions:
            content = content.replace(mention, "")

        return content.strip()[:MAX_INPUT_CHARS]

    @staticmethod
    def get_chat_nick(user_id: int) -> str | None:
        """
        讀取使用者購買的專屬稱呼（/chat_nick 特權）。

        Parameters:
            user_id (int):
                Discord 使用者 ID。

        Returns:
            str | None:
                專屬稱呼，未購買或資料庫無法連線時為 None。
        """

        try:
            connection, cursor = cog.core.sql.link_sql()
            cursor.execute("SELECT nickname FROM chat_nick WHERE uid = %s", (user_id,))
            ret = cursor.fetchall()
            cog.core.sql.end(connection, cursor)

            if ret and ret[0][0]:
                return ret[0][0]
        # 資料庫掛掉不該讓聊天功能跟著掛
        # pylint: disable-next = broad-exception-caught
        except Exception as exception:
            print(f"Error reading chat nick for {user_id}: {exception}")

        return None

    async def _generate_gemini(
        self, model: str, contents: list
    ) -> tuple[str, str, int | None, int | None]:
        """
        呼叫 Gemini 模型。

        Parameters:
            model (str):
                模型名稱。
            contents (list):
                要傳給模型的對話內容。

        Returns:
            tuple[str, str, int | None, int | None]:
                (回覆文字, 實際模型, 輸入 token 數, 輸出 token 數)。
        """

        response = await self.client.aio.models.generate_content(
            model=model,
            contents=contents,
            config=GENERATE_CONFIG,
        )
        usage = response.usage_metadata

        return (
            (response.text or "").strip(),
            response.model_version or model,
            usage.prompt_token_count if usage else None,
            usage.candidates_token_count if usage else None,
        )

    async def _generate_groq(
        self, contents: list
    ) -> tuple[str, str, int | None, int | None]:
        """
        呼叫 Groq（OpenAI 相容介面），把 Gemini 格式的對話轉換過去。

        Parameters:
            contents (list):
                Gemini 格式（types.Content）的對話內容。

        Returns:
            tuple[str, str, int | None, int | None]:
                (回覆文字, 實際模型, 輸入 token 數, 輸出 token 數)。
        """

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        for content in contents:
            messages.append(
                {
                    "role": "assistant" if content.role == "model" else "user",
                    "content": "".join(part.text or "" for part in content.parts),
                }
            )

        response = await self.groq.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            max_tokens=MAX_REPLY_TOKENS,
        )
        usage = response.usage

        return (
            (response.choices[0].message.content or "").strip(),
            response.model,
            usage.prompt_tokens if usage else None,
            usage.completion_tokens if usage else None,
        )

    async def generate(self, contents: list) -> tuple[str, str, int | None, int | None]:
        """
        依序嘗試 Gemini 主模型、Gemini 備援模型、Groq。
        前一層壅塞（500/503）或被限流（429）時退到下一層，
        三層的免費額度各自獨立計算。

        Parameters:
            contents (list):
                要傳給模型的對話內容。

        Returns:
            tuple[str, str, int | None, int | None]:
                (回覆文字, 實際模型, 輸入 token 數, 輸出 token 數)。

        Raises:
            google.genai.errors.APIError:
                所有層都失敗時拋出。
            openai.OpenAIError:
        """

        try:
            return await self._generate_gemini(CHAT_MODEL, contents)
        except google.genai.errors.APIError as exception:
            if exception.code not in (429, 500, 503) or FALLBACK_MODEL == CHAT_MODEL:
                raise

            print(
                f"[chat] {CHAT_MODEL} unavailable ({exception.code}),"
                f" falling back to {FALLBACK_MODEL}"
            )

        try:
            return await self._generate_gemini(FALLBACK_MODEL, contents)
        except google.genai.errors.APIError as exception:
            if self.groq is None or exception.code not in (429, 500, 503):
                raise

            print(
                f"[chat] {FALLBACK_MODEL} unavailable ({exception.code}),"
                f" falling back to {GROQ_MODEL}"
            )

            try:
                return await self._generate_groq(contents)
            except openai.OpenAIError as groq_exception:
                # Groq 也失敗時，把 Gemini 的錯誤往外拋讓 chat() 分類回覆
                print(f"[chat] Groq failed too: {groq_exception}")

                raise exception from groq_exception

    async def chat(self, message: discord.Message, content: str) -> None:
        """
        呼叫 Gemini API 產生回覆並更新頻道對話歷史。

        Parameters:
            message (discord.Message): 觸發的訊息。
            content (str): 清理後的訊息內容。
        """

        channel_history = self.history[message.channel.id]
        # 標上發言者名字，讓模型分得清楚多位使用者；
        # 有買專屬稱呼的人用稱呼取代名字，中電喵就會這樣叫他
        display_name = (
            self.get_chat_nick(message.author.id) or message.author.display_name
        )
        user_content = google.genai.types.Content(
            role="user",
            parts=[
                google.genai.types.Part(text=f"{display_name}：{content}"),
            ],
        )

        try:
            async with message.channel.typing():
                reply_text, model_used, tokens_in, tokens_out = await self.generate(
                    list(channel_history) + [user_content]
                )
        except google.genai.errors.APIError as exception:
            if exception.code == 429:
                # 免費額度的每分鐘上限滿了，約一分鐘後就會恢復
                await message.reply(
                    "太多人同時找我聊天了，等一分鐘再試喵！", mention_author=False
                )
            elif exception.code in (500, 503):
                # Google 端暫時壅塞，過幾分鐘就會恢復
                await message.reply(
                    "現在腦袋有點塞車，等幾分鐘再找我喵！", mention_author=False
                )
            else:
                print(f"Error in chat API: {exception.code} {exception.message}")
                await message.reply("聊天服務出了點問題喵……", mention_author=False)

            return
        # pylint: disable-next = broad-exception-caught
        except Exception as exception:
            print(f"Error in chat: {exception}")
            await message.reply("連不上聊天服務喵……", mention_author=False)

            return

        if not reply_text:
            # 內容被安全機制擋下或沒有產生文字
            await message.reply("這個話題我不方便聊喵……", mention_author=False)

            return

        # 對話成立才寫入歷史，讓後續對話有前後文
        channel_history.append(user_content)
        channel_history.append(
            google.genai.types.Content(
                role="model", parts=[google.genai.types.Part(text=reply_text)]
            )
        )

        # 紀錄 token 用量，方便追蹤免費額度
        print(
            f"[chat] {message.author.id} in={tokens_in}"
            f" out={tokens_out} model={model_used}"
        )

        # Discord 訊息長度上限 2000 字元；
        # sanitize_mentions 破壞 @everyone 等提及解析，
        # allowed_mentions 確保即使殘留 mention 語法也不會真的提及任何人
        await message.reply(
            self.sanitize_mentions(reply_text[:2000]),
            mention_author=False,
            allowed_mentions=discord.AllowedMentions(
                everyone=False, roles=False, users=False
            ),
        )


def setup(bot: discord.Bot) -> None:
    """
    Parameters:
        bot (discord.Bot):
    """

    bot.add_cog(Chat(bot))
