# Future statements
from __future__ import annotations

# Standard imports
import json
import os
import random
import secrets
import time
import traceback
import typing
import urllib.parse

# Third-party imports
import dotenv
import flask
import mysql.connector.abstracts
import requests

# Local imports
import cog.core.sql

app = flask.Flask(__name__)
dotenv.load_dotenv(f"{os.getcwd()}/.env", verbose=True, override=True)

app.secret_key = os.getenv("SECRET_KEY")

# Session cookie hardening: block JS access, restrict cross-site sending, and
# require HTTPS in anything but local debug (set FLASK_DEBUG=true locally to
# test over plain http, e.g. with `flask run`).
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = (
    os.getenv("FLASK_DEBUG", "false").lower() != "true"
)

# How long an OAuth "state" nonce (see /login and /callback) stays valid.
OAUTH_STATE_MAX_AGE_SECONDS = 300

# Upper bound for a single /api/send gift, mirroring the Discord slash-command
# gift path (cog/admin_gift.py) rejecting non-positive counts.
GIFT_AMOUNT_MAX = 100000

discord_client_id = os.getenv("DISCORD_CLIENT_ID")
discord_client_secret = os.getenv("DISCORD_CLIENT_SECRET")
discord_redirect_uri = os.getenv("DISCORD_REDIRECT_URI")
github_client_id = os.getenv("GITHUB_CLIENT_ID")
github_client_secret = os.getenv("GITHUB_CLIENT_SECRET")
github_redirect_uri = os.getenv("GITHUB_REDIRECT_URI")
github_discord_redirect_uri = os.getenv("GITHUB_DISCORD_REDIRECT_URI")
discord_token = os.getenv("DISCORD_TOKEN")
send_gift_role = os.getenv("SEND_GIFT_ROLE")
guild_id = os.getenv("GUILD_ID")

# 將字串轉換為列表
if send_gift_role:
    send_gift_role = [str(role_id) for role_id in send_gift_role.split(",")]
else:
    send_gift_role_list = []


@app.errorhandler(404)
def not_found_error(error) -> tuple[str, typing.Literal[404]]:
    """
    Returns:
        tuple[str, typing.Literal[404]]:
    """

    return flask.render_template("404.html"), 404


def is_safe_redirect_target(target) -> bool:
    """
    Only allow same-site, relative redirect targets after login.

    Rejects anything that could make the browser leave scaict.org: absolute
    URLs, protocol-relative URLs ("//evil.com"), and backslash tricks that
    some browsers still treat as "//" (e.g. "/\\evil.com").

    Parameters:
        target:

    Returns:
        bool:
    """

    if not target or not isinstance(target, str):
        return False

    if not target.startswith("/") or target.startswith(("//", "/\\")):
        return False

    parsed = urllib.parse.urlparse(target)

    return not (parsed.scheme or parsed.netloc)


@app.route("/login")
def login() -> flask.Response:
    """
    Returns:
        flask.Response:
    """

    # state 只用來防 CSRF，跟轉址目標完全脫鉤，並且是伺服器產生、一次性、有時效的亂數。
    state_token = secrets.token_urlsafe(32)
    flask.session["oauth_state"] = state_token
    flask.session["oauth_state_created"] = time.time()

    # redirurl 只允許站內相對路徑（白名單邏輯），並存在 server-side session，
    # 不會被塞進交給 Discord 的 state 參數、也不會被使用者竄改。
    redirurl = flask.request.args.get("redirurl")

    if is_safe_redirect_target(redirurl):
        flask.session["oauth_redirect"] = redirurl
    else:
        flask.session.pop("oauth_redirect", None)

    base_url = "https://discord.com/api/oauth2/authorize"
    params = {
        "client_id": discord_client_id,
        "redirect_uri": discord_redirect_uri,
        "response_type": "code",
        "scope": "identify email",
        "state": state_token,
    }
    # 將參數進行 URL 編碼並組合成最終的 URL
    urlencoded = urllib.parse.urlencode(params)

    return flask.redirect(f"{base_url}?{urlencoded}")


@app.route("/logout")
def logout() -> flask.Response:
    """
    Returns:
        flask.Response:
    """

    flask.session.pop("user", None)

    return flask.redirect(flask.url_for("profile"))


@app.route("/api/mlist")
def listt() -> flask.Response:
    """
    Returns:
        flask.Response:
    """

    if not flask.session:
        return flask.jsonify({"result": "you must login", "status": 403})

    api_admin = flask.session.get(
        "user"
    )  # <class 'werkzeug.local.LocalProxy'> {'avatar': 'https://cdn.discordapp.com/avatars/898141506588770334/a_c81acdd4a925993d053a6fe9ed990c14.png', 'id': '898141506588770334', 'name': 'iach526526'}
    api_admin_id = api_admin.get("id")
    headers = {"Authorization": f"Bot {discord_token}"}
    url = f"https://discord.com/api/v10/guilds/{guild_id}/members/{api_admin_id}"
    response = requests.get(url, headers=headers, timeout=10)
    user_data = response.json()

    if response.status_code != 200:
        return (
            flask.jsonify({"error": "Failed to fetch user information"}),
            response.status_code,
        )

    if send_gift_role not in user_data.get("roles", []):
        return flask.jsonify(
            {"result": "You do not have permission to use this", "status": 403}
        )

    url = "https://discord.com/api/v10/guilds/959823904266944562/members"
    headers = {"Authorization": f"Bot {discord_token}"}
    params = {"limit": 1000}
    response = requests.get(url, headers=headers, params=params, timeout=10)

    return response.json()


@app.route("/api/send/<int:target_user_id>", methods=["POST"])
# POST api/send/{recipient}?gift_type={電電點|抽獎券}count={count}
# POST-only so a cross-site top-level navigation (link/img/redirect) can't
# trigger this as a simple GET request; SameSite=Lax still blocks the cookie
# on cross-site POSTs.
def send(target_user_id) -> flask.Response:
    """
    Parameters:
        target_user_id:

    Returns:
        flask.Response:
    """

    if not flask.session:
        return flask.jsonify({"result": "you must login", "status": 403})

    try:
        api_admin = flask.session.get(
            "user"
        )  # <class 'werkzeug.local.LocalProxy'> {'avatar': 'https://cdn.discordapp.com/avatars/898141506588770334/a_c81acdd4a925993d053a6fe9ed990c14.png', 'id': '898141506588770334', 'name': 'iach526526'}
        api_admin_id = api_admin.get("id")
        api_admin_name = api_admin.get("name")
        discord_api = cog.core.sql.Apis(discord_token, guild_id)
        request_admin = discord_api.get_user(api_admin_id)
        gift_type = flask.request.args.get("gift_type", "電電點")  # 預設為"電電點"
        gift_amount = flask.request.args.get("count", 1)  # 預設數量為1

        if "error" in request_admin:
            # 如果有錯誤，返回錯誤訊息和詳細報錯
            return flask.jsonify(
                {
                    "result": "Failed to fetch user information in admin id",
                    "status": 500,
                    "error_details": request_admin.get("details"),
                }
            )

        admin_roles = request_admin.get("roles", [])

        # 確保發起人有權限發送禮物
        if set(send_gift_role) & set(admin_roles) == set():
            return flask.jsonify(
                {"result": "You do not have permission to use this", "status": 403}
            )

        if gift_type not in ["電電點", "抽獎券"]:
            return flask.jsonify({"result": "Invalid gift type", "status": 400})

        try:
            gift_amount = int(gift_amount)  # 確保 count 是整數
        except ValueError:
            return flask.jsonify({"result": "Invalid count value", "status": 400})

        # 不能發送 0 以下或超過上限的數量，跟 Discord 斜線指令的驗證保持一致
        if not 0 < gift_amount <= GIFT_AMOUNT_MAX:
            return flask.jsonify(
                {
                    "result": f"count must be between 1 and {GIFT_AMOUNT_MAX}",
                    "status": 400,
                }
            )

        # 確保目標用戶存在
        user_data = discord_api.get_user(target_user_id)

        if "error" in user_data:
            # 如果有錯誤，返回錯誤訊息和詳細信息
            return flask.jsonify(
                {
                    "result": "Failed to fetch user information in target id (which is in url path)",
                    "status": 500,
                    "error_details": request_admin.get("details"),
                }
            )

        # 送禮物
        user_name = user_data["user"]["username"]

        try:
            new_gift = cog.core.sql.Gift(
                discord_token, guild_id, target_user_id
            )  # create a new gift object

            if new_gift.dm_room is None:
                return flask.jsonify(
                    {
                        "result": "Failed to create DM channel",
                        "status": 500,
                        "error": new_gift.error_msg,
                    }
                )

            message_id = new_gift.send_gift(gift_type, gift_amount)
            connect, cursor = cog.core.sql.link_sql()

            if not cog.core.sql.user_id_exists(target_user_id, "user", cursor):
                cursor.execute(
                    "INSERT INTO user (uid) VALUE(%s)", (target_user_id,)
                )  # 這裡要調用 api 去抓使用者名稱和 Mail

            cursor.execute(
                "INSERT into gift (btnID,type,count,recipient,received,sender) VALUE(%s,%s,%s,%s,%s,%s)",
                (
                    message_id,
                    gift_type,
                    gift_amount,
                    user_name,
                    True,
                    api_admin_name,
                ),
            )
            gift_type = "point" if gift_type == "電電點" else "ticket"
            query = f"update user set {gift_type}={gift_type}+%s where uid=%s"
            cursor.execute(query, (gift_amount, target_user_id))
            cog.core.sql.end(connect, cursor)
        except Exception as e:
            return flask.jsonify(
                {
                    "result": "internal server error(SQL) when insert gift",
                    "status": 500,
                    "error": str(e),
                }
            )

        return flask.jsonify({"result": "success", "status": 200})
    except Exception as e:
        traceback.print_exc()

        return flask.jsonify(
            {"result": "internal server error", "status": 500, "error": str(e)}
        )


@app.route("/callback")
def callback() -> str | flask.Response:
    """
    Returns:
        str | flask.Response:
    """

    code = flask.request.args.get("code")

    # state 驗證：必須跟 /login 時存進 session 的一次性亂數相符，且沒有過期。
    # 驗證完立刻 pop 掉，確保不能被重放。
    expected_state = flask.session.pop("oauth_state", None)
    state_created = flask.session.pop("oauth_state_created", None)
    provided_state = flask.request.args.get("state")
    state_is_fresh = (
        state_created is not None
        and time.time() - state_created <= OAUTH_STATE_MAX_AGE_SECONDS
    )

    if not expected_state or provided_state != expected_state or not state_is_fresh:
        app.logger.warning(
            "Rejected /callback: invalid or expired OAuth state (ip=%s)",
            flask.request.remote_addr,
        )
        flask.abort(403, description="Invalid or expired OAuth state")

    # 轉址目標只從 server-side session 取得（/login 時已白名單檢查過），
    # 使用者無法透過 state/query string 竄改它。
    redirurl = flask.session.pop("oauth_redirect", None)
    if not is_safe_redirect_target(redirurl):
        redirurl = None

    data = {
        "client_id": discord_client_id,
        "client_secret": discord_client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": discord_redirect_uri,
        "scope": "identify email",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    # pylint: disable-next = missing-timeout
    response = requests.post(
        "https://discord.com/api/oauth2/token", data=data, headers=headers
    )
    access_token = response.json().get("access_token")

    if not access_token:
        return "Error: Access token not found", 400

    headers = {"Authorization": f"Bearer {access_token}"}
    # pylint: disable-next = missing-timeout
    user_response = requests.get("https://discord.com/api/users/@me", headers=headers)
    user_data = user_response.json()

    # 儲存用戶資料到 session
    flask.session["user"] = {
        "name": user_data.get("username"),
        "avatar": (
            f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png"
            if user_data.get("avatar")
            else None
        ),
        "id": user_data.get("id"),
    }

    # 將用戶資料寫入資料庫
    connection, cursor = cog.core.sql.link_sql()
    cog.core.sql.write(user_data["id"], "DCname", user_data["username"], cursor)
    cog.core.sql.write(
        user_data["id"], "DCmail", user_data.get("email", "No email provided"), cursor
    )
    cog.core.sql.end(connection, cursor)

    # 使用者資料已經存進 session["user"]，目標頁面（站內相對路徑）可以直接讀 session，
    # 完全不需要、也絕對不能把 email、user id 或 access token 放進轉址網址。
    if redirurl:
        return flask.redirect(redirurl)

    # 否則，重定向到 profile 頁面
    return flask.redirect(flask.url_for("profile"))


@app.route("/github/discord-callback")
def discord_callback() -> flask.Response:
    """
    Returns:
        flask.Response:
    """

    code = flask.request.args.get("code")
    data = {
        "client_id": discord_client_id,
        "client_secret": discord_client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": github_discord_redirect_uri,
        "scope": "identify",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    # pylint: disable-next = missing-timeout
    response = requests.post(
        "https://discord.com/api/oauth2/token", data=data, headers=headers
    )
    access_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    # pylint: disable-next = missing-timeout
    user_response = requests.get("https://discord.com/api/users/@me", headers=headers)
    user_data = user_response.json()
    flask.session["user"] = {
        "name": user_data["username"],
        "avatar": f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
        "id": user_data["id"],
    }

    return flask.redirect(flask.url_for("star_uwu"))


# make filter static in templates/static static
@app.route("/static/<path:filename>")
def staticfiles(path) -> flask.Response:
    """
    Returns:
        flask.Response:
    """

    return flask.send_from_directory("static", path)


@app.route("/")
def profile() -> str:
    """
    Returns:
        str:
    """

    connection, cursor = cog.core.sql.link_sql()  # SQL 會話
    discord_user = flask.session.get("user")

    if not discord_user:
        cog.core.sql.end(connection, cursor)

        return flask.render_template("home.html")

    user_points = cog.core.sql.read(discord_user["id"], "point", cursor)
    user_tickets = cog.core.sql.read(discord_user["id"], "ticket", cursor)

    if cog.core.sql.user_id_exists(
        discord_user["id"], "user", cursor
    ):  # 有找到這個使用者在表上
        cog.core.sql.end(connection, cursor)

        return flask.render_template(
            "home.html",
            username=discord_user["name"],
            avatar=discord_user["avatar"],
            point=str(user_points),
            ticket=str(user_tickets),
        )

    cog.core.sql.end(connection, cursor)

    return flask.render_template(
        "home.html",
        username=discord_user["name"],
        avatar=discord_user["avatar"],
        point="?",
        ticket="?",
    )


@app.route("/slot")
def slot() -> str:
    """
    Returns:
        str:
    """

    connection, cursor = cog.core.sql.link_sql()  # SQL 會話
    discord_user = flask.session.get("user")

    if not discord_user:
        return flask.render_template("slot.html")

    user_points = cog.core.sql.read(discord_user["id"], "point", cursor)
    user_tickets = cog.core.sql.read(discord_user["id"], "ticket", cursor)

    if cog.core.sql.user_id_exists(
        discord_user["id"], "user", cursor
    ):  # 有找到這個使用者在資料表上
        cog.core.sql.end(connection, cursor)

        return flask.render_template(
            "slot.html",
            username=discord_user["name"],
            avatar=discord_user["avatar"],
            point=str(user_points),
            ticket=str(user_tickets),
        )

    cog.core.sql.end(connection, cursor)

    return flask.render_template(
        "slot.html",
        username=discord_user["name"],
        avatar=discord_user["avatar"],
        point="?",
        ticket="?",
    )


@app.route("/productList")
def product_list() -> typing.Any:
    """
    Returns:
        typing.Any:
    """

    # send pure JSON data
    with open(f"{os.getcwd()}/database/products.json", "r", encoding="utf-8") as file:
        products = json.load(file)

    return products


@app.route("/buyProduct", methods=["POST"])
def buy_product() -> str:
    """
    Returns:
        str:
    """

    # Receive POST request, get product id and check if logged in
    discord_user = flask.session.get("user")

    if not discord_user:
        return "請重新登入"

    product_id = flask.request.json.get("id")  # Convert product_id to a string

    if not product_id:
        return "無法讀取商品 ID"

    with open(f"{os.getcwd()}/database/products.json", "r", encoding="utf-8") as file:
        products = json.load(file)

    # Check in the json array products.products for the product with the id
    product = next((p for p in products["products"] if p["id"] == product_id), None)

    if not product:
        return "商品不存在"

    if product["stock"] < 1:
        return "商品已售完"

    # if pay is not "point"
    if product["pay"] != "point":
        return "此獎品無法使用電電點兌換"

    connection, cursor = cog.core.sql.link_sql()  # SQL 會話

    if not cog.core.sql.user_id_exists(discord_user["id"], "user", cursor):
        cog.core.sql.end(connection, cursor)

        return "使用者不存在"

    user_points = cog.core.sql.read(discord_user["id"], "point", cursor)

    if user_points < product["price"]:
        cog.core.sql.end(connection, cursor)

        return "電電點不足"

    user_points -= product["price"]

    cog.core.sql.write(discord_user["id"], "point", user_points, cursor)
    cog.core.sql.end(connection, cursor)
    product["stock"] -= 1

    with open(f"{os.getcwd()}/database/products.json", "w", encoding="utf-8") as file:
        json.dump(products, file)

    return "購買成功！"


@app.route("/rollSlot", methods=["POST"])
def roll_slot() -> list:
    """
    Returns:
        list:
    """

    data = flask.request.json
    num_draws = int(data.get("numDraws", 1))  # 預設為 1 次抽獎
    connection, cursor = cog.core.sql.link_sql()  # SQL 會話
    discord_user = flask.session.get("user")

    if not discord_user:
        return "請重新登入"

    # # user = users.get(discord_user["id"])
    if not cog.core.sql.user_id_exists(discord_user["id"], "user", cursor):
        cog.core.sql.end(connection, cursor)

        return "使用者不存在"

    with open(f"{os.getcwd()}/database/products.json", "r", encoding="utf-8") as file:
        products = json.load(file)

    # Check in the json array products.products for the product with the id
    product = next((p for p in products["products"] if p["id"] == "slot"), None)
    # product 參考內容 {'name': '貓咪機', 'id': 'slot', 'description': '來抽獎吧', 'price': 1, 'image': 'https://cdn-icons-png.flaticon.com/128/1055/1055823.png', 'stock': 9999, 'category': '遊戲', 'pay': 'ticket', 'url': 'slot'}
    # 用來確認商品是否存在和價格用的
    # 讀使用者的抽獎券和電電點
    user_tickets = cog.core.sql.read(discord_user["id"], "ticket", cursor)
    user_points = cog.core.sql.read(discord_user["id"], "point", cursor)

    if user_tickets < product["price"] * num_draws:
        cog.core.sql.end(connection, cursor)
        easter_egg = (
            "這位好駭客，burp suite 是不能突破我的" if num_draws not in (1, 10) else ""
        )

        return "抽獎券不足\n" + easter_egg

    with open(f"{os.getcwd()}/database/slot.json", "r", encoding="utf-8") as file:
        slot_json = json.load(file)

    for _ in range(num_draws):
        result = random.choices(
            population=slot_json["population"], weights=slot_json["weights"], k=1
        )[0]
        user_points += slot_json["get"][result]
        user_tickets -= product["price"]

    # 更新抽獎券和電電點
    if not discord_user:
        return "請重新登入"

    cog.core.sql.write(discord_user["id"], "ticket", user_tickets, cursor)
    cog.core.sql.write(discord_user["id"], "point", user_points, cursor)
    cog.core.sql.end(connection, cursor)
    easter_egg = (
        f"你是好駭客，破例讓你連抽 {num_draws} 次" if num_draws not in (1, 10) else ""
    )  # 給用 burp suite 偷改前端表單的人一點驚喜

    return [easter_egg + "抽獎成功", slot_json["get"][result], result]


@app.route("/github/login")
def github_login() -> flask.Response:
    """
    GitHub login

    Redirect to GitHub's OAuth login page

    Returns:
        flask.Response:
    """

    # pylint: disable-next = line-too-long
    github_oauth_url = f"https://github.com/login/oauth/authorize?client_id={github_client_id}&scope=user%20repo&redirect_uri={github_redirect_uri}"

    return flask.redirect(github_oauth_url)


@app.route("/github/callback")
def github_callback() -> flask.Response:
    """
    Returns:
        flask.Response:
    """

    # Exchange the authorization code for an access token
    code = flask.request.args.get("code")
    token_url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    data = {
        "client_id": github_client_id,
        "client_secret": github_client_secret,
        "code": code,
    }
    # pylint: disable-next = missing-timeout
    response = requests.post(token_url, headers=headers, data=data)
    flask.session["access_token"] = response.json()["access_token"]

    return flask.redirect(flask.url_for("star_uwu"))


@app.route("/star_uwu")
def star_uwu() -> flask.Response | str | typing.LiteralString:
    """
    Returns:
        flask.Response | str | typing.LiteralString:
    """

    def insert_user(
        user_id,
        table: str,
        cursor: mysql.connector.abstracts.MySQLCursorAbstract | typing.Any,
    ) -> None:  # 初始化（新增）傳入該ID的資料表
        """
        Parameters:
            user_id:
            table (str):
            cursor (mysql.connector.abstracts.MySQLCursorAbstract | typing.Any):
        """

        cursor.execute(f"INSERT INTO {table} (uid) VALUE({user_id})")

    if "access_token" not in flask.session:
        print("GitHub access token not found!")

        return flask.redirect(flask.url_for("github_login"))

    # if dc not login
    discord_user = flask.session.get("user")

    if not discord_user:
        # pylint: disable-next = line-too-long
        return flask.redirect(
            f"https://discord.com/api/oauth2/authorize?client_id={discord_client_id}&redirect_uri={github_discord_redirect_uri}&response_type=code&scope=identify+email"
        )

    # 記錄使用者GitHub
    user_url = "https://api.github.com/user"
    headers = {"Authorization": f"token {flask.session['access_token']}"}
    # pylint: disable-next = missing-timeout
    user_response = requests.get(user_url, headers=headers)
    github_username = user_response.json()["login"]
    github_email = user_response.json()["email"]
    connection, cursor = cog.core.sql.link_sql()  # SQL 會話
    discord_user = flask.session.get("user")
    cog.core.sql.write(discord_user["id"], "githubName", github_username, cursor)
    cog.core.sql.write(discord_user["id"], "githubMail", github_email, cursor)
    cog.core.sql.end(connection, cursor)

    repo_owner = "SCAICT"
    repo_name = "SCAICT-uwu"
    star_url = f"https://api.github.com/user/starred/{repo_owner}/{repo_name}"
    headers = {"Authorization": f"token {flask.session['access_token']}"}
    # Sending a PUT request to star the repository
    # pylint: disable-next = missing-timeout
    response = requests.put(star_url, headers=headers)

    # Checking the response status and returning an appropriate message
    if response.ok:
        print(f"Successfully starred {repo_owner}/{repo_name}! {response}")
        connection, cursor = cog.core.sql.link_sql()  # SQL 會話

        if not cog.core.sql.user_id_exists(
            discord_user["id"], "user", cursor
        ):  # 該 user id 不在user表格內，插入該筆使用者資料
            insert_user(discord_user["id"], "user", cursor)

        # if already starred. loveuwu is 1
        if cog.core.sql.read(discord_user["id"], "loveuwu", cursor):
            cog.core.sql.end(connection, cursor)

            return flask.render_template("already.html")

        cog.core.sql.write(discord_user["id"], "loveuwu", 1, cursor)
        user_points = cog.core.sql.read(discord_user["id"], "point", cursor)
        user_points += 20
        cog.core.sql.write(discord_user["id"], "point", user_points, cursor)
        cog.core.sql.end(connection, cursor)

        return flask.render_template("star_success.html")

    return f"Failed to star {repo_owner}/{repo_name}."


if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.run(debug=True)
