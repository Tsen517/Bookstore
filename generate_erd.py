from eralchemy import render_er

# 資料庫檔案路徑
db_path = 'sqlite:///database.db'

# 產生 ERD 圖檔（PDF 或 PNG）
render_er(db_path, 'erd_diagram.pdf')  # 也可改成 'erd_diagram.png'