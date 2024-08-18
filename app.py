# Standard imports
import json
import os
import random

# Third-party imports
from flask import Flask, redirect, request, session, url_for, render_template, send_from_directory
import requests

# Local imports
from cog.core.sql import write
from cog.core.sql import read
from cog.core.sql import link_sql
from cog.core.sql import end
from cog.core.sql import user_id_exists

app = Flask(__name__)

# FILEPATH: /d:/GayHub/SCAICT-Discord-Bot/token.json
with open(f"{os.getcwd()}/token.json", encoding = "utf-8") as token_file:
    token_data = json.load(token_file)

app.secret_key = token_data["secret_key"]
discord_client_id = token_data["discord_client_id"]
discord_client_secret = token_data["discord_client_secret"]
discord_redirect_uri = token_data["discord_redirect_uri"]
github_client_id = token_data["github_client_id"]
github_client_secret = token_data["github_client_secret"]
github_redirect_uri = token_data["github_redirect_uri"]
github_discord_redirect_uri = token_data["github_discord_redirect_uri"]

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.route("/login")
def login():
    # pylint: disable-next = line-too-long
    return redirect(f"https://discord.com/api/oauth2/authorize?client_id={discord_client_id}&redirect_uri={discord_redirect_uri}&response_type=code&scope=identify+email")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("profile"))

@app.route("/callback")
def callback():
    code = request.args.get("code")
    data = {
        "client_id": discord_client_id,
        "client_secret": discord_client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": discord_redirect_uri,
        "scope": "identify"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    # pylint: disable-next = missing-timeout
    response = requests.post("https://discord.com/api/oauth2/token", data = data, headers = headers)
    access_token = response.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    # pylint: disable-next = missing-timeout
    user_response = requests.get("https://discord.com/api/users/@me", headers = headers)
    user_data = user_response.json()
    session["user"] = {
        "name": user_data["username"],
        "avatar": f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
        "id": user_data["id"]
    }
    connection, cursor = link_sql()
    write(user_data["id"], "DCname", user_data["username"], cursor)
    #email
    write(user_data["id"], "DCmail", user_data["email"], cursor)

    end(connection, cursor)
    return redirect(url_for("profile"))

@app.route("/github/discord-callback")
def discord_callback():
    code = request.args.get("code")
    data = {
        "client_id": discord_client_id,
        "client_secret": discord_client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": github_discord_redirect_uri,
        "scope": "identify"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    # pylint: disable-next = missing-timeout
    response = requests.post("https://discord.com/api/oauth2/token", data = data, headers = headers)
    print(response.json())
    access_token = response.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    # pylint: disable-next = missing-timeout
    user_response = requests.get("https://discord.com/api/users/@me", headers = headers)
    user_data = user_response.json()
    session["user"] = {
        "name": user_data["username"],
        "avatar": f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
        "id": user_data["id"]
    }
    return redirect(url_for("star_uwu"))

# make filder static in templates/static static
@app.route("/static/<path:filename>")
def staticfiles(path):
    return send_from_directory("static", path)

@app.route("/")
def profile():
    connection, cursor = link_sql() # SQL 會話
    discord_user = session.get("user")
    if not discord_user:
        end(connection, cursor)
        return render_template("home.html")

    user_points = read(discord_user["id"], "point", cursor)
    user_tickets = read(discord_user["id"], "ticket", cursor)
    if user_id_exists(discord_user["id"], "USER", cursor): # 有找到這個使用者在表上
        end(connection, cursor)
        return render_template(
            "home.html",
            username = discord_user["name"],
            avatar = discord_user["avatar"],
            point = str(user_points),
            ticket = str(user_tickets)
        )

    end(connection, cursor)
    return render_template(
        "home.html",
        username = discord_user["name"],
        avatar = discord_user["avatar"],
        point = "?",
        ticket = "?"
    )

@app.route("/slot")
def slot():
    connection, cursor = link_sql() # SQL 會話
    discord_user = session.get("user")
    if not discord_user:
        return render_template("slot.html")
    user_points = read(discord_user["id"], "point", cursor)
    user_tickets = read(discord_user["id"], "ticket", cursor)
    if user_id_exists(discord_user["id"], "USER", cursor): # 有找到這個使用者在資料表上
        end(connection, cursor)
        return render_template(
            "slot.html",
            username = discord_user["name"],
            avatar = discord_user["avatar"],
            point = str(user_points),
            ticket = str(user_tickets)
        )

    end(connection, cursor)
    return render_template(
        "slot.html",
        username = discord_user["name"],
        avatar = discord_user["avatar"],
        point = "?",
        ticket = "?"
    )

@app.route("/productList")
def product_list():
    # send pure JSON data
    with open(f"{os.getcwd()}/DataBase/products.json", "r", encoding = "utf-8") as file:
        products = json.load(file)
    return products

@app.route("/buyProduct", methods = [ "POST" ])
def buy_product():
    # Recieve POST request, get product id and check if logged in
    discord_user = session.get("user")
    if not discord_user:
        return "請重新登入"
    product_id = request.json.get("id") # Convert product_id to a string
    if not product_id:
        return "無法讀取商品 ID"
    with open(f"{os.getcwd()}/DataBase/products.json", "r", encoding = "utf-8") as file:
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

    connection, cursor = link_sql() # SQL 會話

    if not user_id_exists(discord_user["id"], "USER", cursor):
        end(connection, cursor)
        return "使用者不存在"
    user_points = read(discord_user["id"], "point", cursor)
    if user_points < product["price"]:
        end(connection, cursor)
        return "電電點不足"
    user_points -= product["price"]

    write(discord_user["id"], "point", user_points, cursor)
    end(connection, cursor)
    product["stock"] -= 1
    with open(f"{os.getcwd()}/DataBase/products.json", "w", encoding = "utf-8") as file:
        json.dump(products, file)
    return "購買成功！"

@app.route("/rollSlot", methods = [ "POST" ])
def roll_slot():
    data = request.json
    num_draws = int(data.get("numDraws", 1))  # 預設為 1 次抽獎
    connection, cursor = link_sql() # SQL 會話
    discord_user = session.get("user")
    if not discord_user:
        return "請重新登入"

    # # user = users.get(discord_user["id"])
    if not user_id_exists(discord_user["id"], "USER", cursor):
        end(connection, cursor)
        return "使用者不存在"
    with open(f"{os.getcwd()}/DataBase/products.json", "r", encoding = "utf-8") as file:
        products = json.load(file)
    # Check in the json array products.products for the product with the id

    product = next((p for p in products["products"] if p["id"] == "slot"), None)
    # product 參考內容 {'name': '貓咪機', 'id': 'slot', 'description': '來抽獎吧', 'price': 1, 'image': 'https://cdn-icons-png.flaticon.com/128/1055/1055823.png', 'stock': 9999, 'category': '遊戲', 'pay': 'ticket', 'url': 'slot'}
    # 用來確認商品是否存在和價格用的
    
    # 讀使用者的抽獎券和電電點
    user_tickets = read(discord_user["id"], "ticket", cursor)
    user_points = read(discord_user["id"], "point", cursor)
    if user_tickets < product["price"]*num_draws:
        end(connection, cursor)
        easter_egg="這位好駭客，burp suite 是不能突破我的" if num_draws not in (1,10) else ""
        return "抽獎券不足\n"+easter_egg
    with open(f"{os.getcwd()}/DataBase/slot.json", "r", encoding = "utf-8") as file:
        slot_json = json.load(file)
    for _ in range(num_draws):
        result = random.choices(
            population = slot_json["population"],
            weights = slot_json["weights"],
            k = 1
        )[0]
        user_points += slot_json["get"][result]
        user_tickets -= product["price"]
    # 更新抽獎券和電電點
    if not discord_user:
        return "請重新登入"
    write(discord_user["id"], "ticket", user_tickets, cursor)
    write(discord_user["id"], "point", user_points, cursor)
    end(connection, cursor)
    easter_egg=f"你是好駭客，破例讓你連抽 {num_draws} 次" if num_draws not in (1,10) else ""#給用 burp suite 偷改前端表單的人一點驚喜
    return [ easter_egg+"抽獎成功", slot_json["get"][result], result ]

# GitHub login

@app.route("/github/login")
def github_login():
    # Redirect to GitHub's OAuth login page
    # pylint: disable-next = line-too-long
    github_oauth_url = f"https://github.com/login/oauth/authorize?client_id={github_client_id}&scope=user%20repo&redirect_uri={github_redirect_uri}"
    return redirect(github_oauth_url)

@app.route("/github/callback")
def github_callback():
    # Exchange the authorization code for an access token
    code = request.args.get("code")
    token_url = "https://github.com/login/oauth/access_token"
    headers = { "Accept": "application/json" }
    data = {
        "client_id": github_client_id,
        "client_secret": github_client_secret,
        "code": code
    }
    # pylint: disable-next = missing-timeout
    response = requests.post(token_url, headers = headers, data = data)
    print(response.json())
    session["access_token"] = response.json()["access_token"]

    return redirect(url_for("star_uwu"))

@app.route("/star_uwu")
def star_uwu():
    def insert_user(user_id, table, cursor): # 初始化（新增）傳入該ID的資料表
        cursor.execute(f"INSERT INTO {table} (uid) VALUE({user_id})")

    if "access_token" not in session:
        print("GitHub access token not found!")
        return redirect(url_for("github_login"))
    # if dc not loggin
    discord_user = session.get("user")
    if not discord_user:
        # pylint: disable-next = line-too-long
        return redirect(f"https://discord.com/api/oauth2/authorize?client_id={discord_client_id}&redirect_uri={github_discord_redirect_uri}&response_type=code&scope=identify+email")
    # 記錄使用者GitHub
    user_url = "https://api.github.com/user"
    headers = { "Authorization": f"token {session['access_token']}" }
    # pylint: disable-next = missing-timeout
    user_response = requests.get(user_url, headers = headers)
    print(user_response.json())
    github_username = user_response.json()["login"]
    github_email = user_response.json()["email"]
    connection, cursor = link_sql() # SQL 會話
    discord_user = session.get("user")
    write(discord_user["id"], "githubName", github_username, cursor)
    write(discord_user["id"], "githubMail", github_email, cursor)
    end(connection, cursor)

    repo_owner = "SCAICT"
    repo_name = "SCAICT-uwu"
    star_url = f"https://api.github.com/user/starred/{repo_owner}/{repo_name}"
    headers = { "Authorization": f"token {session['access_token']}" }
    print(session['access_token'])
    # Sending a PUT request to star the repository
    # pylint: disable-next = missing-timeout
    response = requests.put(star_url, headers = headers)
    print(response.text)
    # Checking the response status and returning an appropriate message
    if response.ok:
        print(f"Successfully starred {repo_owner}/{repo_name}! {response}")
        connection, cursor = link_sql() # SQL 會話
        if not user_id_exists(discord_user["id"], "USER", cursor): # 該 uesr id 不在USER表格內，插入該筆使用者資料
            insert_user(discord_user["id"], "USER", cursor)
        # if already starred. liveuwu is 1
        if read(discord_user["id"], "loveuwu", cursor):
            end(connection, cursor)
            return render_template("already.html")
        write(discord_user["id"], "loveuwu", 1, cursor)
        user_points = read(discord_user["id"], "point", cursor)
        user_points += 20
        write(discord_user["id"], "point", user_points, cursor)
        end(connection, cursor)
        return render_template("star_success.html")

    return f"Failed to star {repo_owner}/{repo_name}."

if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug = True)
