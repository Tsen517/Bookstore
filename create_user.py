import sqlite3

conn = sqlite3.connect('database.db')

# 以 email 為例，將該用戶設為管理員
conn.execute('UPDATE users SET isAdmin = 1 WHERE email = ?', ('admin@gmail.com',))

conn.commit()
conn.close()