# SCAICT-Discord-Bot

* main.py: Discord Bot
* app.py: Flask Web App
* generate-secrets.py: 生成 Secret Key，請貼至 token.json
* Database MySQL:使用外部伺服器，相關設定在cog/core/secret.py
## token.json

```json
{
    "token":"",
    "secret_key":"",
    "client_id":"",
    "client_secret":"",
    "redirect_uri":"http://127.0.0.1:5000/callback"
}
```

## Slot

<database/slot.json>

```
 {
    "項目": [機率,獲得數量]
 }
 ```
## credits

<a href="https://www.flaticon.com/free-icons/slot-machine" title="slot machine icons">Slot machine icons created by Freepik - Flaticon</a>