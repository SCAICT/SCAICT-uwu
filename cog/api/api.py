import requests
class Apis:
    def __init__(self, api_key:str,guild_id:int):
        self.api_key = api_key
        self.guild_id = guild_id
        self.headers = {"Authorization": f"Bot {self.api_key}","Content-Type": "application/json",}
    def get_user(self, uid):
        """API 回傳的資料格式範例，已經把一些敏感資料隱藏掉
                {
            "avatar": null,
            "banner": null,
            "communication_disabled_until": null,
            "flags": 0,
            "joined_at": "",
            "nick": null,
            "pending": false,
            "premium_since": null,
            "roles": [
                "12348763",
                "12448763",
                "12548763"
            ],
            "unusual_dm_activity_until": null,
            "user": {
                "id": "",
                "username": "",
                "avatar": "",
                "discriminator": "0",
                "public_flags": 256,
                "flags": 256,
                "banner": "",
                "accent_color": 2054367,
                "global_name": "",
                "avatar_decoration_data": {
                    "asset": "a_d3da36040163ee0f9176dfe7ced45cdc",
                    "sku_id": "1144058522808614923",
                    "expires_at": null
                },
                "banner_color": "#1f58df",
                "clan": null
            },
            "mute": false,
            "deaf": false
        }
        
        """
        url = f"https://discord.com/api/v10/guilds/{self.guild_id}/members/{uid}"
        response = requests.get(url, headers=self.headers,timeout=5)
        if response.status_code != 200:
            return []
        return response.json()