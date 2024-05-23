from cog.core.sql import link_sql
from cog.core.sql import end
connection, cursor=link_sql()
cursor.execute("use CTF;")
cursor.execute("SELECT title,score FROM data")
res=cursor.fetchall()
print(res)

end(connection, cursor)