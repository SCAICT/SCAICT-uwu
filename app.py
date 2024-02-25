from flask import Flask, redirect, request, session, url_for, render_template
import requests
import json

app = Flask(__name__)

# FILEPATH: /d:/GayHub/SCAICT-Discord-Bot/token.json
with open("token.json") as file:
    data = json.load(file)

app.secret_key = data["secret_key"]
client_id = data["client_id"]
client_secret = data["client_secret"]
redirect_uri = data["redirect_uri"]

@app.route("/")
def index():
    return redirect(f"https://discord.com/api/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=identify")

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

@app.route("/profile")
def profile():
    DcUser = session.get("user")
    if DcUser:
        # get file from datebase/users.json and read point and tickets
        with open("database/users.json") as file:
            users = json.load(file)
        user = users.get(DcUser["id"])
        if user:
            return render_template("home.html", username=DcUser["name"], avatar=DcUser["avatar"], point=user["point"], ticket=user["ticket"])
        else:
            return render_template("home.html", username=DcUser["name"], avatar=DcUser["avatar"], point="?", ticket="?")
    else:
        return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
