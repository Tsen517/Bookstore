import sqlite3

conn = sqlite3.connect('database.db')

# 1. 清空 users 資料表
conn.execute('DELETE FROM users')
conn.commit()

# 2. 重設 AUTOINCREMENT 計數器
conn.execute('DELETE FROM sqlite_sequence WHERE name="users"')
conn.commit()

# 3. 僅新增一筆資料（userId 會自動為 1）
user1 = ('1234', 'hhh@example.com', 'User', 'One', '地址1', '', '100', '台北市', '台北市', '台灣', '0911111111', 0)
conn.execute('''
INSERT INTO users (password, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone, isAdmin)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', user1)
conn.commit()

conn.close()