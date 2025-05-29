import sqlite3

conn = sqlite3.connect('database.db')

# 新增一筆使用者資料（含 isAdmin 欄位）
user = ('0000', 'test@gmail.com', 'Test', 'User', 'PU University', '', '433', '台南市', '台南市', '台灣', '0966888777', 0)

conn.execute('''
INSERT INTO users (password, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone, isAdmin)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', user)

conn.commit()
conn.close()