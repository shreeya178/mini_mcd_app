from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(basedir, 'database.db')

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database initialization
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS menu
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS cart
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, item_id INTEGER, quantity INTEGER)''')
    conn.commit()
    conn.close()

init_db()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            flash('Login successful!')
            return redirect(url_for('menu'))
        else:
            flash('Invalid credentials!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/menu')
def menu():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM menu")
    items = c.fetchall()
    conn.close()
    return render_template('menu.html', items=items)

@app.route('/add_to_cart/<int:item_id>')
def add_to_cart(item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO cart (user_id, item_id, quantity) VALUES (?, ?, 1)", (user_id, item_id))
    conn.commit()
    conn.close()
    flash('Item added to cart!')
    return redirect(url_for('menu'))

@app.route('/cart')
def cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Fetch cart items
    c.execute('''
        SELECT menu.id, menu.name, menu.price, menu.image, cart.quantity 
        FROM cart 
        JOIN menu ON cart.item_id = menu.id 
        WHERE cart.user_id = ?
    ''', (user_id,))
    items = c.fetchall()
    
    # Calculate total amount
    c.execute('''
        SELECT SUM(menu.price * cart.quantity) 
        FROM cart 
        JOIN menu ON cart.item_id = menu.id 
        WHERE cart.user_id = ?
    ''', (user_id,))
    total_amount = c.fetchone()[0] or 0  # Default to 0 if cart is empty
    
    conn.close()
    return render_template('cart.html', items=items, total_amount=total_amount)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO menu (name, price) VALUES (?, ?)", (name, price))
        conn.commit()
        conn.close()
        flash('Item added to menu!')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM menu")
    items = c.fetchall()
    conn.close()
    return render_template('admin.html', items=items)

@app.route('/remove_item/<int:item_id>')
def remove_item(item_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM menu WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    flash('Item removed from menu!')
    return redirect(url_for('admin'))

@app.route('/place_order')
def place_order():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    try:
        # Calculate total amount
        c.execute('''
            SELECT SUM(menu.price * cart.quantity) 
            FROM cart 
            JOIN menu ON cart.item_id = menu.id 
            WHERE cart.user_id = ?
        ''', (user_id,))
        total_amount = c.fetchone()[0]
        
        if total_amount is None:
            flash('Your cart is empty!', 'error')
            return redirect(url_for('cart'))
        
        # Insert order into orders table
        c.execute("INSERT INTO orders (user_id, total_amount) VALUES (?, ?)", (user_id, total_amount))
        
        # Clear the user's cart
        c.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
        
        conn.commit()
        flash('Order placed successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'An error occurred: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('cart'))

if __name__ == '__main__':
    app.run(debug=False)