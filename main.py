from flask import *
import sqlite3, hashlib, os
from werkzeug.utils import secure_filename
from db import query_db, execute_db, get_all_products, get_all_categories, get_items_by_category
import requests

app = Flask(__name__)
app.secret_key = 'random string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def getLoginDetails():
    if 'email' not in session:
        return False, '', 0
    user = query_db("SELECT userId, firstName FROM users WHERE email = ?", (session['email'],), one=True)
    if not user:
        return False, '', 0
    userId, firstName = user
    noOfItems = query_db("SELECT count(productId) FROM kart WHERE userId = ?", (userId,), one=True)[0]
    return True, firstName, noOfItems

# 直接呼叫
itemData = get_all_products()
categoryData = get_all_categories()

@app.route("/")
def root():
    loggedIn, firstName, noOfItems = getLoginDetails()
    itemData = get_all_products()
    categoryData = get_all_categories()
    itemData = parse(itemData)
    return render_template("home.html", itemData=itemData, categoryData=categoryData, show_category_btn=True, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/add")
def admin():
    if not session.get('isAdmin'):
        return redirect(url_for('root'))
    categories = get_all_categories()
    return render_template('add.html', categories=categories)

@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    if request.method == "POST":
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        category = request.form['category']
        author = request.form.get('author', '')  # 新增這行
        # 新增類別處理
        if category == "add_new":
            new_category = request.form['new_category'].strip()
            if new_category:
                execute_db("INSERT INTO categories (name) VALUES (?)", (new_category,))
                categoryId = query_db("SELECT categoryId FROM categories WHERE name = ?", (new_category,), one=True)[0]
            else:
                categoryId = 1
        else:
            categoryId = int(category)
        imagename = request.form.get('image', '')
        try:
            execute_db(
                '''INSERT INTO products (name, price, description, image, stock, categoryId, author) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (name, price, description, imagename, stock, categoryId, author)
            )
            msg = "added successfully"
        except Exception as e:
            msg = "error occured"
        print(msg)
        return redirect(url_for('root'))

@app.route("/remove")
def remove():
    data = get_all_products()
    return render_template('remove.html', data=data)

@app.route("/removeItem", methods=["POST"])
def removeItem():
    if not session.get('isAdmin'):
        return redirect(url_for('root'))
    productId = request.form.get('productId')
    if productId:
        try:
            execute_db("DELETE FROM products WHERE productId = ?", (productId,))
        except Exception as e:
            print("刪除失敗:", e)
    return redirect(url_for('manageProducts'))

@app.route('/displayCategory')
def display_category():
    categoryId = request.args.get('categoryId')
    itemData = get_items_by_category(categoryId)
    categoryData = get_all_categories()
    loggedIn, firstName, noOfItems = getLoginDetails()
    itemData = parse(itemData)
    return render_template(
        'home.html',
        itemData=itemData,
        categoryData=categoryData,
        show_category_btn=True,
        loggedIn=loggedIn,
        firstName=firstName,
        noOfItems=noOfItems
    )

@app.route("/account/profile")
def profileHome():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    profileData = query_db("SELECT userId, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone FROM users WHERE email = ?", (session['email'],), one=True)
    return render_template("profileHome.html", profileData=profileData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/account/profile/edit")
def editProfile():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    profileData = query_db("SELECT userId, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone FROM users WHERE email = ?", (session['email'],), one=True)
    return render_template("editProfile.html", profileData=profileData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/account/profile/changePassword", methods=["GET", "POST"])
def changePassword():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    if request.method == "POST":
        oldPassword = request.form['oldpassword']
        oldPassword = hashlib.md5(oldPassword.encode()).hexdigest()
        newPassword = request.form['newpassword']
        newPassword = hashlib.md5(newPassword.encode()).hexdigest()
        user = query_db("SELECT userId, password FROM users WHERE email = ?", (session['email'],), one=True)
        if user:
            userId, password = user
            if (password == oldPassword):
                try:
                    execute_db("UPDATE users SET password = ? WHERE userId = ?", (newPassword, userId))
                    msg = "Changed successfully"
                except Exception as e:
                    msg = "Failed"
                return render_template("changePassword.html", msg=msg)
            else:
                msg = "Wrong password"
                return render_template("changePassword.html", msg=msg)
        else:
            msg = "User not found"
            return render_template("changePassword.html", msg=msg)
    else:
        return render_template("changePassword.html")

@app.route("/updateProfile", methods=["GET", "POST"])
def updateProfile():
    if request.method == 'POST':
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1']
        address2 = request.form['address2']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']
        try:
            execute_db(
                'UPDATE users SET firstName = ?, lastName = ?, address1 = ?, address2 = ?, zipcode = ?, city = ?, state = ?, country = ?, phone = ? WHERE email = ?',
                (firstName, lastName, address1, address2, zipcode, city, state, country, phone, email)
            )
            msg = "Saved Successfully"
        except Exception as e:
            msg = "Error occured"
        return redirect(url_for('editProfile'))

@app.route("/loginForm")
def loginForm():
    if 'email' in session:
        return redirect(url_for('root'))
    else:
        return render_template('login.html', error='')

@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = query_db("SELECT userId, password, isAdmin FROM users WHERE email = ?", (email,), one=True)
        if user and user[1] == hashlib.md5(password.encode()).hexdigest():
            session['email'] = email
            session['userId'] = user[0]
            session['isAdmin'] = user[2]  # 新增
            return redirect(url_for('root'))
        else:
            error = 'Invalid UserId / Password'
            return render_template('login.html', error=error)

@app.route("/productDescription")
def productDescription():
    loggedIn, firstName, noOfItems = getLoginDetails()
    productId = request.args.get('productId')
    productData = query_db('SELECT productId, name, price, description, image, stock, author FROM products WHERE productId = ?', (productId,), one=True)
    return render_template("productDescription.html", data=productData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/addToCart")
def addToCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    else:
        productId = int(request.args.get('productId'))
        user = query_db("SELECT userId FROM users WHERE email = ?", (session['email'],), one=True)
        if user:
            userId = user[0]
            try:
                execute_db("INSERT INTO kart (userId, productId) VALUES (?, ?)", (userId, productId))
                msg = "Added successfully"
            except Exception as e:
                msg = "Error occured"
        return redirect(url_for('root'))

@app.route("/cart")
def cart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    email = session['email']
    user = query_db("SELECT userId FROM users WHERE email = ?", (email,), one=True)
    if user:
        userId = user[0]
        products = query_db("SELECT products.productId, products.name, products.price, products.image FROM products, kart WHERE products.productId = kart.productId AND kart.userId = ?", (userId,))
        totalPrice = sum(row[2] for row in products)
    else:
        products = []
        totalPrice = 0
    return render_template("cart.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/removeFromCart")
def removeFromCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    email = session['email']
    productId = int(request.args.get('productId'))
    user = query_db("SELECT userId FROM users WHERE email = ?", (email,), one=True)
    if user:
        userId = user[0]
        try:
            execute_db("DELETE FROM kart WHERE userId = ? AND productId = ?", (userId, productId))
            msg = "removed successfully"
        except Exception as e:
            msg = "error occured"
    return redirect(url_for('root'))

@app.route("/logout")
def logout():
    session.pop('email', None)
    session.pop('userId', None)
    session.pop('isAdmin', None)
    return redirect(url_for('root'))

def is_valid(email, password):
    data = query_db('SELECT email, password FROM users')
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False

@app.route("/checkout", methods=['GET','POST'])
def payment():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    email = session['email']
    user = query_db("SELECT userId FROM users WHERE email = ?", (email,), one=True)
    if user:
        userId = user[0]
        products = query_db("SELECT products.productId, products.name, products.price, products.image FROM products, kart WHERE products.productId = kart.productId AND kart.userId = ?", (userId,))
        totalPrice = sum(row[2] for row in products)
        for row in products:
            execute_db("INSERT INTO Orders (userId, productId) VALUES (?, ?)", (userId, row[0]))
            # 新增這一行，扣減庫存
            execute_db("UPDATE products SET stock = stock - 1 WHERE productId = ?", (row[0],))
        execute_db("DELETE FROM kart WHERE userId = ?", (userId,))
    else:
        products = []
        totalPrice = 0
    return render_template("checkout.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        password = request.form['password']
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1']
        address2 = request.form['address2']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']
        try:
            execute_db(
                'INSERT INTO users (password, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName, address1, address2, zipcode, city, state, country, phone)
            )
            msg = "Registered Successfully"
        except Exception as e:
            msg = "Error occured"
        return render_template("login.html", error=msg)

@app.route("/registerationForm")
def registrationForm():
    return render_template("register.html")

@app.route("/account/profile/view")
def viewProfile():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    profileData = query_db("SELECT userId, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone FROM users WHERE email = ?", (session['email'],), one=True)
    return render_template("viewProfile.html", profileData=profileData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/admin/orders")
def admin_orders():
    # 僅管理員可檢視所有訂單
    if not session.get('isAdmin'):
        return redirect(url_for('root'))
    orders = query_db("""
        SELECT Orders.orderId, users.email, products.name, Orders.productId
        FROM Orders
        JOIN users ON Orders.userId = users.userId
        JOIN products ON Orders.productId = products.productId
    """)
    return render_template("admin_orders.html", orders=orders)

@app.route("/orders")
def user_orders():
    # 僅登入用戶可檢視自己的訂單
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    user = query_db("SELECT userId FROM users WHERE email = ?", (session['email'],), one=True)
    if not user:
        return redirect(url_for('root'))
    userId = user[0]
    orders = query_db("""
        SELECT Orders.orderId, products.name, Orders.productId
        FROM Orders
        JOIN products ON Orders.productId = products.productId
        WHERE Orders.userId = ?
    """, (userId,))
    return render_template("user_orders.html", orders=orders)

@app.route("/manageProducts")
def manageProducts():
    if not session.get('isAdmin'):
        return redirect(url_for('root'))
    data = get_all_products()
    return render_template('manageProducts.html', data=data)

@app.route("/updateProduct", methods=["POST"])
def updateProduct():
    if not session.get('isAdmin'):
        return redirect(url_for('root'))
    productId = request.form['productId']
    price = float(request.form['price'])
    stock = int(request.form['stock'])
    try:
        execute_db(
            "UPDATE products SET price = ?, stock = ? WHERE productId = ?",
            (price, stock, productId)
        )
        msg = "Updated successfully"
    except Exception as e:
        msg = "Error occurred"
    print(msg)
    return redirect(url_for('manageProducts'))

@app.route("/admin/search_books", methods=["GET", "POST"])
def search_books():
    if not session.get('isAdmin'):
        return redirect(url_for('root'))
    books = []
    if request.method == "POST":
        keyword = request.form['keyword']
        resp = requests.get(f"https://openlibrary.org/search.json?q={keyword}&limit=10")
        if resp.ok:
            docs = resp.json().get('docs', [])
            for book in docs:
                if not book.get('title'):
                    continue
                work_key = book.get('key')
                description = get_description(work_key) if work_key else "無簡介"
                image = ""
                if book.get('cover_i'):
                    image = f"https://covers.openlibrary.org/b/id/{book['cover_i']}-L.jpg"
                author = ""
                if book.get('author_name'):
                    author = ', '.join(book['author_name'])
                books.append({
                    "title": book['title'],
                    "author": author,
                    "price": 300,
                    "description": description,
                    "image": image,
                })
    return render_template(
        "search_books.html",
        books=books,
        get_all_categories=get_all_categories
    )

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans

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

@app.route("/admin")
def admin_center():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    return render_template("admin.html", loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

if __name__ == '__main__':
    app.run(debug=True)
