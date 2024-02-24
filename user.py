import json

# 讀寫使用者資料到json檔案的函式給 cog 使用

blankUser = {
            "point": 0,
            "charge_combo": 0,
            "last_charge": "1970-01-01",
            "next_lottery": 7,
            "num_comment": 0,
            "last_comment": "1970-01-01",
            "num_comment_point": {"times": 2, "next_reward": 1}
        }

def write(userId, property, value):
    with open('./database/users.json', 'r') as file:
        data=json.load(file)
    if str(userId) not in data:
        data[str(userId)] = blankUser
    data[str(userId)][property] = value
    with open('./users.json', 'w') as f:
        json.dump(data, f, indent=4)
    return True

def read(userId, property):
    with open('./database/users.json', 'r') as file:
        data=json.load(file)
    if str(userId) not in data:
        data[str(userId)] = blankUser
    return data[str(userId)][property]