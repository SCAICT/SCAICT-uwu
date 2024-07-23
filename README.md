<!-- markdownlint-disable first-line-h1 -->
<!-- markdownlint-disable html -->

<div align="center">
<img src="uwu.png" width="200px" alt="中電喵 SCAICT uwu">

# 中電喵 SCAICT uwu

住在中電會 Discord 伺服器的貓咪

[![同步代辦事項至 Notion](https://github.com/SCAICT/SCAICT-uwu/actions/workflows/notion.yml/badge.svg?event=issues)](https://github.com/SCAICT/SCAICT-uwu/actions/workflows/notion.yml)
[![官方網站](https://img.shields.io/website?label=官方網站&&url=https%3A%2F%2Fscaict.org%2F)](https://scaict.org/)
[![中電商店](https://img.shields.io/website?label=中電商店&&url=https%3A%2F%2Fstore.scaict.org%2F)](https://store.scaict.org/)
[![加入 Discord 伺服器](https://img.shields.io/discord/959823904266944562?label=Discord&logo=discord&)](https://dc.scaict.org)
[![追蹤 Instagram](https://img.shields.io/badge/follow-%40scaict.tw-pink?&logo=instagram)](https://www.instagram.com/scaict.tw/)

</div>

> 這個專案目前處於開發階段，並且可能會有一些問題。如果您發現了任何問題或有任何建議，請透過提交問題來通知我們。

## 如何部署？

1. 克隆此倉庫。
2. 在 Python 3.11 中建立環境。
3. 安裝依賴套件。

   ```bash
   pip install -r requirements.txt
   ```

4. 在 `DataBase/server.config.json` 中設定頻道。
5. 啟動 SQL 伺服器。
6. 在 Breadcrumbs SCAICT-uwu 的 `cog/core/sql_acc.py` 中設定 SQL 伺服器。
7. 執行 Flask。

   ```bash
   flask run
   ```

8. 執行 `main.py`。

   ```bash
   python main.py
   ```

## 檔案

* `main.py`：中電喵。
* `app.py`：中電商店。
* `generate_secrets.py`：為 `app.py` 產生密鑰，執行後儲存在 `token.json` 中。
* 資料庫 MySQL：使用外部伺服器，相關設定在 `cog/core/secret.py` 中。
* `token.json`：

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

* `DataBase/slot.json`：

  設定老虎機的中獎機率。

  ```json
  {
      "element": [ percentage, reward ]
  }
  ```

## 鳴謝

中電喵是由中電會和[貢獻者們](https://github.com/SCAICT/SCAICT-uwu/graphs/contributors)共同開發和維護的專案。角色設計由[毛哥 EM](https://elvismao.com/) 和[瑞樹](https://www.facebook.com/ruishuowo)創作，而部分圖示則選用了來自 [Freepik - Flaticon](https://www.flaticon.com/free-icons/slot-machine) 的設計素材。
