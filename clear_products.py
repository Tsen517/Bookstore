import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute("DELETE FROM products")
conn.commit()
conn.close()
print("products 資料表已清空")