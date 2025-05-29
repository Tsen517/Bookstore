import sqlite3

conn = sqlite3.connect('database.db')

# 取得第一筆和第三筆 userId
cursor = conn.execute('SELECT userId FROM users ORDER BY userId ASC')
user_ids = [row[0] for row in cursor.fetchall()]

if len(user_ids) >= 3:
    conn.execute('DELETE FROM users WHERE userId = ?', (user_ids[0],))
    conn.execute('DELETE FROM users WHERE userId = ?', (user_ids[2],))

conn.commit()
conn.close()