from flask import Flask, redirect, request, session, url_for, render_template, send_from_directory
import requests
import json
import random
import os
from cog.core.SQL import write
from cog.core.SQL import read
from cog.core.SQL import linkSQL
from cog.core.SQL import end
from cog.core.SQL import isExist

app = Flask(__name__)

# FILEPATH: /d:/GayHub/SCAICT-Discord-Bot/token.json
with open(f"{os.getcwd()}/token.json", encoding='utf-8') as file:
    data = json.load(file)

app.secret_key = data["secret_key"]
discord_client_id = data["discord_client_id"]
discord_client_secret = data["discord_client_secret"]
discord_redirect_uri = data["discord_redirect_uri"]
github_client_id = data["github_client_id"]
github_client_secret = data["github_client_secret"]
github_redirect_uri = data["github_redirect_uri"]
github_discord_redirect_uri = data["github_discord_redirect_uri"]

@app.route("/login")
def login():
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
    response = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
    access_token = response.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    user_response = requests.get("https://discord.com/api/users/@me", headers=headers)
    user_data = user_response.json()
    session["user"] = {
        "name": user_data["username"],
        "avatar": f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
        "id": user_data["id"]
    }
    CONNECTION,CURSOR=linkSQL()
    write(user_data["id"],"DCname",user_data["username"],CURSOR)
    #email
    write(user_data["id"],"DCmail",user_data["email"],CURSOR)

    end(CONNECTION,CURSOR)
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
    response = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
    print(response.json())
    access_token = response.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    user_response = requests.get("https://discord.com/api/users/@me", headers=headers)
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
    CONNECTION,CURSOR=linkSQL()#SQL 會話
    DcUser = session.get("user")
    if not DcUser:
        end(CONNECTION,CURSOR)
        return render_template("home.html")

    yourPoints=read(DcUser["id"],"point",CURSOR)
    yourTicket=read(DcUser["id"],"ticket",CURSOR)
    if isExist(DcUser["id"],"USER",CURSOR):#有找到這個使用者在表上
        end(CONNECTION,CURSOR)
        return render_template("home.html", username=DcUser["name"], avatar=DcUser["avatar"], point=str(yourPoints), ticket=str(yourTicket))
    else:
        end(CONNECTION,CURSOR)
        return render_template("home.html", username=DcUser["name"], avatar=DcUser["avatar"], point="?", ticket="?")

@app.route("/slot")
def slot():
    CONNECTION,CURSOR=linkSQL()#SQL 會話
    DcUser = session.get("user")
    if not DcUser:
        return render_template("slot.html")
    yourPoints=read(DcUser["id"],"point",CURSOR)
    yourTicket=read(DcUser["id"],"ticket",CURSOR)
    if isExist(DcUser["id"],"USER",CURSOR):#有找到這個使用者在表上
        end(CONNECTION,CURSOR)
        return render_template("slot.html", username=DcUser["name"], avatar=DcUser["avatar"], point=str(yourPoints), ticket=str(yourTicket))
    else:
        end(CONNECTION,CURSOR)
        return render_template("slot.html", username=DcUser["name"], avatar=DcUser["avatar"], point="?", ticket="?")

@app.route("/productList")
def productList():
    # send pure json data
    with open(f"{os.getcwd()}/DataBase/products.json", 'r', encoding='utf-8') as file:
        products = json.load(file)
    return products

@app.route("/buyProduct", methods=["POST"])
def buyProduct():
    # Recieve POST request, get product id and check if logged in
    DcUser = session.get("user")
    if not DcUser:
        return "請重新登入"
    product_id = request.json.get("id")  # Convert product_id to a string
    if not product_id:
        return "無法讀取商品 ID"
    with open(f"{os.getcwd()}/DataBase/products.json", 'r', encoding='utf-8') as file:
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


    CONNECTION,CURSOR=linkSQL()#SQL 會話

    if not (isExist(DcUser["id"],"USER",CURSOR)):
        end(CONNECTION,CURSOR)
        return "用戶不存在"
    yourPoint=read(DcUser["id"],"point",CURSOR)
    if yourPoint < product["price"]:
        end(CONNECTION,CURSOR)
        return "電電點不足"
    yourPoint -= product["price"]

    write(DcUser["id"],"point",yourPoint,CURSOR)
    end(CONNECTION,CURSOR)
    product["stock"] -= 1
    with open(f"{os.getcwd()}/DataBase/products.json", "w", encoding='utf-8') as file:
        json.dump(products, file)
    return "購買成功!"

@app.route("/rollSlot", methods=["GET"])
def rollSlot():
    CONNECTION,CURSOR=linkSQL()#SQL 會話
    DcUser = session.get("user")
    if not DcUser:
        return "請重新登入"

    # user = users.get(DcUser["id"])
    if not (isExist(DcUser["id"],"USER",CURSOR)):
        end(CONNECTION,CURSOR)
        return "用戶不存在"
    with open(f"{os.getcwd()}/DataBase/products.json", 'r', encoding='utf-8') as file:
        products = json.load(file)
    # Check in the json array products.products for the product with the id
    product = next((p for p in products["products"] if p["id"] == "slot"), None)

    #讀用戶的抽獎券和電電點
    yourTicket=read(DcUser["id"],"ticket",CURSOR)
    yourPoint=read(DcUser["id"],"point",CURSOR)
    if yourTicket < product["price"]:
        end(CONNECTION,CURSOR)
        return "抽獎券不足"
    with open(f"{os.getcwd()}/DataBase/slot.json", 'r', encoding='utf-8') as file:
        slot_json = json.load(file)
    result = random.choices(
        population=slot_json["population"],
        weights=slot_json["weights"],
        k=1
    )[0]
    yourPoint += slot_json["get"][result]
    yourTicket -= product["price"]
    #更新抽獎券和電電點
    write(DcUser["id"],"ticket",yourTicket,CURSOR)
    write(DcUser["id"],"point",yourPoint,CURSOR)
    end(CONNECTION,CURSOR)
    return ["抽獎成功", slot_json["get"][result], result]

# GitHUb Login

@app.route("/github/login")
def github_login():
    # Redirect to GitHub's OAuth login page
    github_oauth_url = f"https://github.com/login/oauth/authorize?client_id={github_client_id}&scope=user%20repo&redirect_uri={github_redirect_uri}"
    return redirect(github_oauth_url)

@app.route("/github/callback")
def github_callback():
    # Exchange the authorization code for an access token
    code = request.args.get("code")
    token_url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    data = {
        "client_id": github_client_id,
        "client_secret": github_client_secret,
        "code": code
    }
    response = requests.post(token_url, headers=headers, data=data)
    print(response.json())
    session["access_token"] = response.json()["access_token"]



    return redirect(url_for("star_uwu"))

@app.route("/star_uwu")
def star_uwu():
    def insertUser(userId,TABLE,CURSOR):#初始化(創建)傳入該ID的表格
        CURSOR.execute(f"INSERT INTO {TABLE} (uid) VALUE({userId})")

    if "access_token" not in session:
        print("GitHub access token not found!")
        return redirect(url_for("github_login"))
    # if dc not loggin
    DcUser = session.get("user")
    if not DcUser:
        return redirect(f"https://discord.com/api/oauth2/authorize?client_id={discord_client_id}&redirect_uri={github_discord_redirect_uri}&response_type=code&scope=identify+email")
    #紀錄用戶Github
    user_url = "https://api.github.com/user"
    headers = {"Authorization": f"token {session['access_token']}"}
    user_response = requests.get(user_url, headers=headers)
    print(user_response.json())
    github_username = user_response.json()["login"]
    github_mail = user_response.json()["email"]
    CONNECTION,CURSOR=linkSQL()#SQL 會話
    DcUser = session.get("user")
    write(DcUser["id"],"githubName",github_username,CURSOR)
    write(DcUser["id"],"githubMail",github_mail,CURSOR)
    end(CONNECTION,CURSOR)

    repo_owner = "SCAICT"
    repo_name = "SCAICT-uwu"
    star_url = f"https://api.github.com/user/starred/{repo_owner}/{repo_name}"
    headers = {"Authorization": f"token {session['access_token']}"}
    print(session['access_token'])
    # Sending a PUT request to star the repository
    response = requests.put(star_url, headers=headers)
    print(response.text)
    # Checking the response status and returning an appropriate message
    if response.ok:
        print(f"Successfully starred {repo_owner}/{repo_name}! {response}")
        CONNECTION,CURSOR=linkSQL()#SQL 會話
        if not(isExist(DcUser["id"],"USER",CURSOR)):#該 uesr id 不在USER表格內，插入該筆用戶資料
            insertUser(DcUser["id"],"USER",CURSOR)
        # if already starred. liveuwu is 1
        if read(DcUser["id"],"loveuwu",CURSOR):
            end(CONNECTION,CURSOR)
            return render_template("already.html")
        write(DcUser["id"],"loveuwu",1,CURSOR)
        yourPoint=read(DcUser["id"],"point",CURSOR)
        yourPoint += 20
        write(DcUser["id"],"point",yourPoint,CURSOR)
        end(CONNECTION,CURSOR)
        return render_template("star_success.html")
    else:
        return f"Failed to star {repo_owner}/{repo_name}."

if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)