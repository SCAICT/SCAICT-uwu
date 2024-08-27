import os
import requests
from dotenv import load_dotenv
import json

load_dotenv(f"{os.getcwd()}/.env",verbose=True, override=True)

discord_token = os.getenv("DISCORD_TOKEN")
guild_ID = os.getenv("GUILD_ID")
uid=input("Enter the user ID: ")

headers = {"Authorization": f"Bot {discord_token}"}
url = f"https://discord.com/api/v10/guilds/{guild_ID}/members/{uid}"
response = requests.get(url, headers=headers,timeout=5)
result = response.json()
print(json.dumps(result, indent=4))  # type: ignore
