import sqlite3

conn = sqlite3.connect('database.db')

# 新增多筆分類資料
categories = [
    ('Novel',),
    ('programming',),
    ('psychology',),
    ('self growth',)
]

conn.executemany('INSERT INTO categories (name) VALUES (?)', categories)

conn.commit()
conn.close()