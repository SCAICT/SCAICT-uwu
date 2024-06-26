
<div align="center">
<img src=uwu.png width=200px alt="中電喵 SCAICT uwu">

# 中電喵 SCAICT uwu

住在中電會 Discord 伺服器的貓咪

[![同步代辦事項至 Notion](https://github.com/SCAICT/SCAICT-uwu/actions/workflows/notion.yml/badge.svg?event=issues)](https://github.com/SCAICT/SCAICT-uwu/actions/workflows/notion.yml)
[![Website](https://img.shields.io/website?label=官方網站&&url=https%3A%2F%2Fscaict.org%2F)](https://scaict.org/)
[![中電商店](https://img.shields.io/website?label=中電商店&&url=https%3A%2F%2Fstore.scaict.org%2F)](https://store.scaict.org/)
[![Discord](https://img.shields.io/discord/959823904266944562?label=Discord&logo=discord&)](https://dc.scaict.org)
[![Instagram Follow](https://img.shields.io/badge/follow-%40scaict.tw-pink?&logo=instagram)](https://www.instagram.com/scaict.tw/)

</div>

> 這個項目目前處於開發階段，並且可能會有一些問題。如果您發現了任何問題或有任何建議，請通過提交問題來通知我們。

## 如何部屬?

1. Clone this repo.
2. Create Python environment in 3.11.
3. Install dependencies.

   ```bash
   pip install flask py-cord mysql-connector-python requests
   ```

4. Config channels in `DataBase/server.config.json` .
5. Run SQL Server
6. Config SQL Server in Breadcrumbs SCAICT-uwu `cog/core/sql_acc.py`

7. Run Flask

   ```bash
   flask run
   ```

8. Run main.py

   ```bash
   python main.py
   ```

## 檔案

* `main.py` : Discord Bot
* `app.py` : Flask web app
* `generate_secrets.py` : Generate secret key for app.py. Run and save it in token.json
* Database MySQL: 使用外部伺服器，相關設定在cog/core/secret.py
* `token.json` :

  ```json
  {
      "discord_token": "",
      "secret_key": "",
      "discord_client_id": "",
      "discord_client_secret": "",
      "discord_redirect_uri": "http://127.0.0.1:5000/callback",
      "github_client_id": "",
      "github_client_secret": "",
      "github_redirect_uri": "http://127.0.0.1:5000/github/callback",
      "github_discord_redirect_uri": "http://127.0.0.1:5000/github/discord-callback"
  }
  ```

* `database/slot.json` :\
  Set the possibility for slot machine.

  ```json
  {
      "element": [ percentage, reward ]
  }
  ```


## 鳴謝

中電喵是由中電會和 [貢獻者們](https://github.com/SCAICT/SCAICT-uwu/graphs/contributors) 共同開發和維護的項目。角色設計由 [毛哥EM](https://elvismao.com/) 和 [瑞樹](https://www.facebook.com/ruishuowo) 創作，而部分圖標則選用了來自 [Freepik - Flaticon](https://www.flaticon.com/free-icons/slot-machine) 的設計素材。