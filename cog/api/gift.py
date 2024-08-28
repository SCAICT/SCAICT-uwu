import requests

class Gift:
    def __init__(self, api_key: str, guild_id: int,recipient_id:int):
        self.api_key = api_key
        self.guild_id = guild_id
        self.error_msg = None
        self.headers = {
            "Authorization": f"Bot {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            fetch_usr = self.__new_dm(recipient_id)["id"]
            if "id" in fetch_usr:
                self.dm_room = fetch_usr["id"]
            else:
                self.dm_room = None
        except Exception as e:
            self.dm_room = None
            self.error_msg = str(e)
        print(self.dm_room)
    def __new_dm(self, uid: int)->dict:
        try:
            url = f"https://discord.com/api/v10/users/@me/channels"
            payload = {
                "recipient_id": uid
            }
            #{'id': '', 'type': 1, 'last_message_id': '1276230139230814241', 'flags': 0, 'recipients': [{'id': '', 'username': '', 'avatar': '', 'discriminator': '0', 'public_flags': 256, 'flags': 256, 'banner': '', 'accent_color': 2054367, 'global_name': '', 'avatar_decoration_data': {'asset': '', 'sku_id': '1144058522808614923', 'expires_at': None}, 'banner_color': '#1f58df', 'clan': None}]}
            response = requests.post(url, headers=self.headers, json=payload, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"result": "interal server error", "status": 500, "error": str(e)}
        except Exception as e:
            return {"result": "interal server error", "status": 500, "error": str(e)}
    