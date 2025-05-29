import sqlite3

conn = sqlite3.connect('database.db')

# 依據 email 刪除一位使用者
conn.execute('DELETE FROM users WHERE email = ?', ('test@gmail.com',))

conn.commit()
conn.close()