import sqlite3

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Drop existing tables (if they exist)
c.execute("DROP TABLE IF EXISTS users")
c.execute("DROP TABLE IF EXISTS menu")
c.execute("DROP TABLE IF EXISTS cart")
c.execute("DROP TABLE IF EXISTS orders")

# Create Users Table
c.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0
    )
''')

# Create Menu Table
c.execute('''
    CREATE TABLE menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        image TEXT NOT NULL
    )
''')

# Create Cart Table
c.execute('''
    CREATE TABLE cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        quantity INTEGER DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (item_id) REFERENCES menu (id)
    )
''')

# Create Orders Table
c.execute('''
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        total_amount REAL NOT NULL,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')

# Insert Admin User (username: admin, password: admin123)
c.execute("INSERT OR IGNORE INTO users (username, password, is_admin) VALUES (?, ?, ?)", 
          ('admin', 'admin123', 1))

# Insert Sample Menu Items (Only 4 items)
menu_items = [
    ('Burger', 5.99, 'burger.jpg'),
    ('Coke', 1.99, 'coke.jpg'),
    ('Fries', 3.99, 'fries.jpg'),
    ('Puff', 2.99, 'puff.jpg')
]
c.executemany("INSERT OR IGNORE INTO menu (name, price, image) VALUES (?, ?, ?)", menu_items)

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database initialized successfully!")