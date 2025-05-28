import requests
import sqlite3

def fetch_books(limit=10):
    url = f"https://openlibrary.org/search.json?q=self+growth&limit=30"  # 多抓一些以便篩選
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()["docs"]

def get_description(work_key):
    url = f"https://openlibrary.org{work_key}.json"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            desc = data.get("description", "")
            if isinstance(desc, dict):
                return desc.get("value", "")
            elif isinstance(desc, str):
                return desc
    except Exception:
        pass
    return "無簡介"

def insert_books(books, need_count=10):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    inserted = 0
    for book in books:
        if inserted >= need_count:
            break
        title = book.get("title", "").strip()
        author = ", ".join(book.get("author_name", [])).strip()
        work_key = book.get("key", "")
        description = get_description(work_key) if work_key else ""
        price = 300
        stock = 10
        cover_id = book.get("cover_i")
        image = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else ""
        categoryId = 4  
        name = f"{title} - {author}"

        # 判斷任一必要欄位為空就跳過
        if not (title and author and description and image):
            continue

        cur.execute(
            "INSERT INTO products (name, price, description, image, stock, categoryId) VALUES (?, ?, ?, ?, ?, ?)",
            (name, price, description, image, stock, categoryId)
        )
        inserted += 1
    conn.commit()
    conn.close()
    print(f"已寫入 {inserted} 筆自我成長相關書籍到 products 資料表。")

if __name__ == "__main__":
    books = fetch_books()
    insert_books(books, need_count=10)