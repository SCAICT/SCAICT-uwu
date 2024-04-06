# 中電喵 SCAICT uwu

A cat living in SCAICT Discord server.

[![Sync issues to Notion](https://github.com/SCAICT/SCAICT-uwu/actions/workflows/notion.yml/badge.svg?event=issues)](https://github.com/SCAICT/SCAICT-uwu/actions/workflows/notion.yml)

![中電喵 SCAICT uwu](thumbnail.png)

> This project is still in beta. If you have any problem, it works on my machine.

## How to run?

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

## Files

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

## Credits

Made by SCAICT.

[Slot machine icons created by Freepik - Flaticon](https://www.flaticon.com/free-icons/slot-machine)
