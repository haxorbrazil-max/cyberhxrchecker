import sqlite3
from config import DATABASE_PATH
def connect():
    c=sqlite3.connect(DATABASE_PATH); c.row_factory=sqlite3.Row; return c
def init_db():
    c=connect()
    c.executescript('''
    CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY,name TEXT,username TEXT,balance_cents INTEGER DEFAULT 0,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT,category TEXT,name TEXT,description TEXT,price_cents INTEGER,enabled INTEGER DEFAULT 1);
    CREATE TABLE IF NOT EXISTS stock(id INTEGER PRIMARY KEY AUTOINCREMENT,product_id INTEGER,identifier TEXT,code5 TEXT,code34 TEXT,fictional_name TEXT,number10 TEXT,value_cents INTEGER,sold INTEGER DEFAULT 0);
    CREATE TABLE IF NOT EXISTS gifts(code TEXT PRIMARY KEY,value_cents INTEGER,used INTEGER DEFAULT 0);
    CREATE TABLE IF NOT EXISTS transactions(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,provider_transaction_id TEXT UNIQUE,amount_cents INTEGER,state TEXT,transaction_type TEXT,credited INTEGER DEFAULT 0);
    CREATE TABLE IF NOT EXISTS purchases(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,product_id INTEGER,stock_id INTEGER,amount_cents INTEGER);
    '''); c.commit(); c.close()
