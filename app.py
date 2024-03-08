from flask import Flask, redirect, request, session, url_for, render_template, send_from_directory
import requests
import json
import random
from cog.core.SQL import write
from cog.core.SQL import read
from cog.core.SQL import linkSQL
from cog.core.SQL import end
from cog.core.SQL import isExist
app = Flask(__name__)

# FILEPATH: /d:/GayHub/SCAICT-Discord-Bot/token.json
with open("token.json", encoding='utf-8') as file:
    data = json.load(file)

app.secret_key = data["secret_key"]
client_id = data["client_id"]
client_secret = data["client_secret"]
redirect_uri = data["redirect_uri"]

@app.route("/login")
def login():
    return redirect(f"https://discord.com/api/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=identify")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("profile"))

@app.route("/callback")
def callback():
    code = request.args.get("code")
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
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
    return redirect(url_for("profile"))

# make filder static in templates/static static
@app.route("/static/<path:filename>")
def staticfiles(path):
    return send_from_directory("static", path)

@app.route("/")
def profile():
    CONNECTION,CURSOR=linkSQL()#SQL 會話
    DcUser = session.get("user")
    if not DcUser:
        return render_template("home.html")
    # with open("database/users.json", encoding='utf-8') as file:
    #     users = json.load(file)
    # user = users.get(DcUser["id"])
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
    # with open("database/users.json", encoding='utf-8') as file:
    #     users = json.load(file)
    # user = users.get(DcUser["id"])
    yourPoints=read(DcUser["id"],"point",CURSOR)
    yourTicket=read(DcUser["id"],"ticket",CURSOR)
    end(CONNECTION,CURSOR)
    if isExist(DcUser["id"],"USER",CURSOR):#有找到這個使用者在表上
        return render_template("slot.html", username=DcUser["name"], avatar=DcUser["avatar"], point=str(yourPoints), ticket=str(yourTicket))
    else:
        return render_template("slot.html", username=DcUser["name"], avatar=DcUser["avatar"], point="?", ticket="?")

@app.route("/productList")
def productList():
    # send pure json data
    with open("database/products.json", 'r', encoding='utf-8') as file:
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
    with open("database/products.json", 'r', encoding='utf-8') as file:
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
    # with open("database/users.json") as file:
    #     users = json.load(file)
    # user = users.get(DcUser["id"])
    
    CONNECTION,CURSOR=linkSQL()#SQL 會話
    
    if not (isExist(DcUser["id"],"USER",CURSOR)):
        return "用戶不存在"
    yourPoint=read(DcUser["id"],"point",CURSOR)
    if yourPoint < product["price"]:
        return "電電點不足"
    yourPoint -= product["price"]
    # with open("database/users.json", "w", encoding='utf-8') as file:
    #     json.dump(users, file)
    write(DcUser["id"],"point",yourPoint,CURSOR)
    end(CONNECTION,CURSOR)
    product["stock"] -= 1
    with open("database/products.json", "w", encoding='utf-8') as file:
        json.dump(products, file)
    return "購買成功!"

@app.route("/rollSlot", methods=["GET"])
def rollSlot():
    CONNECTION,CURSOR=linkSQL()#SQL 會話
    DcUser = session.get("user")
    if not DcUser:
        return "請重新登入"
    # with open("database/users.json", encoding='utf-8') as file:
    #     users = json.load(file)
    # user = users.get(DcUser["id"])
    if not (isExist(DcUser["id"],"USER",CURSOR)):
        return "用戶不存在"
    with open("database/products.json", 'r', encoding='utf-8') as file:
        products = json.load(file)
    # Check in the json array products.products for the product with the id
    product = next((p for p in products["products"] if p["id"] == "slot"), None)
    
    #讀用戶的抽獎券和電電點
    yourTicket=read(DcUser["id"],"ticket",CURSOR)
    yourPoint=read(DcUser["id"],"point",CURSOR)
    if yourTicket < product["price"]:
        return "抽獎券不足"
    with open("database/slot.json", 'r', encoding='utf-8') as file:
        slot_json = json.load(file)
    result = random.choices(
        population=slot_json["population"],
        weights=slot_json["weights"],
        k=1
    )[0]
    yourPoint += slot_json["get"][result]
    yourTicket -= product["price"]
    # with open("database/users.json", "w", encoding='utf-8') as file:
    #     json.dump(users, file)
    #更新抽獎券和電電點
    write(DcUser["id"],"ticket",yourTicket)
    write(DcUser["id"],"point",yourPoint)
    
    return ["抽獎成功", slot_json["get"][result], result]

if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)
