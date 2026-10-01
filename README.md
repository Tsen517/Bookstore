# Bookstore 線上書店

一個以 Flask 製作的簡易電子商務網站，提供書籍瀏覽、購物車、結帳、訂單查詢，以及管理員後台功能。

## 技術架構

| 層級 | 技術 |
| --- | --- |
| 前端 | HTML + CSS + JavaScript（`templates/` 為純 HTML 模板，`static/` 放少量 CSS / JS） |
| 後端 | Python 3 + Flask（Jinja2 模板渲染） |
| 資料庫 | SQLite（`database.db`） |
| 外部資料 | [Open Library API](https://openlibrary.org/developers/api)（用來抓取書籍資料） |

## 使用的 API

本專案使用 [Open Library API](https://openlibrary.org/developers/api)（免費、免金鑰）取得書籍資料，共呼叫三個端點：

| 端點 | 用途 | 使用位置 |
| --- | --- | --- |
| `GET https://openlibrary.org/search.json?q={關鍵字}&limit={筆數}` | 依關鍵字搜尋書籍，取得書名（`title`）、作者（`author_name`）、作品代碼（`key`）、封面編號（`cover_i`） | `fetch_books.py`（每個分類抓 30 筆）、`main.py` 的 `/admin/search_books`（抓 10 筆） |
| `GET https://openlibrary.org{work_key}.json` | 依作品代碼取得書籍簡介（`description`，可能是字串或含 `value` 的物件），逾時 5 秒，取不到時顯示「無簡介」 | `get_description()`（`fetch_books.py`、`main.py`） |
| `https://covers.openlibrary.org/b/id/{cover_id}-M.jpg`（或 `-L.jpg`） | 書籍封面圖片，直接以網址存入 `products.image` | `fetch_books.py`（M 尺寸）、管理員搜尋頁（L 尺寸） |

**資料處理規則**
- 書名、作者、簡介、封面任一欄位為空的書會被略過，確保寫入的資料完整。
- 每個分類固定寫入 10 筆；價格預設 300、庫存預設 10。
- 書名以 `書名 - 作者` 的格式存入 `products.name`。

## 個人負責項目

- **Open Library API 串接**：負責 `fetch_books.py` 批次匯入書籍，以及管理員後台 `/admin/search_books` 的書籍搜尋，包含 API 請求、JSON 解析、簡介與封面處理、缺漏資料過濾。
- **資料庫基本查詢**：負責 `db.py`，封裝 `query_db`、`execute_db`（使用參數化查詢）以及 `get_all_products`、`get_all_categories`、`get_items_by_category` 等常用查詢，供 `main.py` 各路由共用。

## 專案結構

```
.
├─ main.py            # Flask 主程式（所有路由）
├─ db.py              # 資料庫存取工具（query_db / execute_db 等）
├─ database.py        # 建立資料表
├─ fetch_books.py     # 從 Open Library 抓書並寫入 products
├─ generate_erd.py    # 產生 ERD 圖（erd_diagram.pdf）
├─ diagram.txt        # 網站路由 / 頁面架構圖
├─ erd_diagram.pdf    # 資料庫 ERD
├─ database.db        # SQLite 資料庫檔
├─ templates/         # HTML 模板
└─ static/            # CSS、JS 與上傳圖片（static/uploads）
```

## 功能

**一般使用者**
- 註冊 / 登入 / 登出
- 首頁書籍列表、依分類瀏覽、商品詳情
- 加入購物車、移除商品、購物車結帳
- 單本書直接購買（Buy Direct）
- 個人資料檢視與編輯、修改密碼
- 查看自己的訂單

**管理員**
- 新增 / 移除書籍（可同時新增分類）
- 商品管理（修改價格與庫存）
- 檢視所有訂單、所有會員，並可刪除會員
- 透過 Open Library 搜尋書籍資料

> 管理員功能需要帳號的 `isAdmin` 欄位為 `1`。

完整的頁面與路由對照請參考 [`diagram.txt`](diagram.txt)。

## 資料庫

資料表共 5 張：`users`、`products`、`categories`、`kart`（購物車）、`Orders`（訂單）。
關聯圖請見 [`erd_diagram.pdf`](erd_diagram.pdf)。

| 資料表 | 說明 |
| --- | --- |
| `users` | 會員資料（含 `isAdmin` 管理員旗標） |
| `products` | 書籍（名稱、價格、簡介、圖片、庫存、作者、分類） |
| `categories` | 書籍分類 |
| `kart` | 購物車，每筆為一位使用者加入的一本書 |
| `Orders` | 訂單，每筆為一位使用者購買的一本書 |

## 環境需求

1. Python 3
2. Flask
3. SQLite（Python 內建 `sqlite3`，無需另外安裝）
4. requests（呼叫 Open Library API 用）
5. eralchemy（選用，僅產生 ERD 圖時需要）

## 安裝與執行

```bash
# 1. 建立並啟用虛擬環境
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. 安裝套件
pip install flask requests
pip install eralchemy           # 選用，產生 ERD 用

# 3. 建立資料庫（專案已附 database.db，若要重建才需要）
python database.py

# 4. 補上後來新增的欄位（見下方「資料庫注意事項」）

# 5. （選用）從 Open Library 匯入範例書籍
python fetch_books.py

# 6. 啟動網站
python main.py
```

啟動後，在瀏覽器開啟 <http://localhost:5000>。

## 資料庫注意事項

`database.py` 建立的 `users` 與 `products` 資料表**不含** `isAdmin` 與 `author` 欄位，但程式（`main.py`、`fetch_books.py`）與 ERD 都有使用。若從零重建資料庫，請在執行 `database.py` 後補上：

```bash
sqlite3 database.db "ALTER TABLE users ADD COLUMN isAdmin INTEGER DEFAULT 0;"
sqlite3 database.db "ALTER TABLE products ADD COLUMN author TEXT;"
```

並先建立分類資料（`fetch_books.py` 預設使用 1~4 號分類：Novel、programming、psychology、self growth）：

```bash
sqlite3 database.db "INSERT INTO categories (categoryId, name) VALUES (1,'Novel'),(2,'programming'),(3,'psychology'),(4,'self growth');"
```

## 建立管理員帳號

1. 在網站上先以一般流程註冊一個帳號。
2. 將該帳號設為管理員：

```bash
sqlite3 database.db "UPDATE users SET isAdmin = 1 WHERE email = 'your@email.com';"
```

3. 重新登入後即可使用管理員功能（`/admin`）。

## 產生 ERD 圖

```bash
python generate_erd.py
```

會依據 `database.db` 產生 `erd_diagram.pdf`（需先安裝 eralchemy 與 Graphviz）。
