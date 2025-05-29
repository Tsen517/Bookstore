import sqlite3

DB_PATH = 'database.db'

def query_db(query, args=(), one=False):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(query, args)
        rv = cur.fetchall()
        return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(query, args)
        conn.commit()

def get_all_products():
    return query_db('SELECT productId, name, price, description, image, stock FROM products')

def get_all_categories():
    return query_db('SELECT categoryId, name FROM categories')

def get_items_by_category(categoryId):
    return query_db("SELECT * FROM products WHERE categoryId = ?", (categoryId,))

