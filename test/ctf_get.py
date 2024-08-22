# 把舊 CTF JSON 格式檔案的資料搬進資料庫，執行時拿到資料夾根木錄才能正確import SQL
# Standard imports
import json

# Local imports
from cog.core.sql import link_sql
from cog.core.sql import end

with open("./DataBase/ctf.json", "r", encoding="utf-8") as file:
    # code to read and process the file goes here
    file = json.load(file)
    connection, cursor = link_sql()
    cursor.execute("USE `CTF`")

    for questionId, ctf in file.items():
        # questionId 是題目ID
        # ctf 包含該題目的所有屬性，等等再用鍵值分離出來
        # cursor.execute(f"INSERT INTO `data`(id,flags,score,restrictions,message_id,case_status,start_time,end_time,title,tried) VALUES({questionId},'{ctf['flag']}',{ctf['score']},'{ctf['limit']}',{ctf['messageId']},{ctf['case']},'{ctf['start']}','{ctf['end']}','{ctf['title']}','{ctf['tried']}');")
        for h in ctf["history"]:
            solved = 1 if int(h) in ctf["solved"] else 0
            cursor.execute(
                f"INSERT INTO `history`(data_id,uid,count,solved) VALUES('{questionId}',{h},{ctf['history'][h]},{solved});"
            )

        end(connection, cursor)
        break
