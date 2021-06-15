import sqlite3

class SqliteHelper:

    def __init__(self, name = None):
        self.conn = None
        self.cursor = None

        if name:
            self.open(name)
    
    def open(self, name):
        try:
            self.conn = sqlite3.connect(name)
            self.cursor = self.conn.cursor()
            sqlite3.version
        except sqlite3.Error as e:
            print("Failed connecting to database...")
    
    def create_table(self):
        c = self.cursor
        c.execute("""CREATE TABLE license_plates(
                    id INTEGER,
                    type TEXT,
                    symbols_plate TEXT,
                    region INTEGER,
                    date REAL,
                    media BLOB,
                    PRIMARY KEY("id" AUTOINCREMENT)
                )""")    
    
    def edit(self, query, updates): #UPDATE
        c = self.cursor
        c.execute(query, updates)
        self.conn.commit()
    
    def delete(self, query): #DELETE
        c = self.cursor
        c.execute(query)
        self.conn.commit()
    
    def insert(self, query, inserts): #INSERT
        c = self.cursor
        c.execute(query, inserts)
        self.conn.commit()
    
    def select(self, query): #SELECT
        c = self.cursor
        try:
            c.execute(query)
        except sqlite3.OperationalError:
            self.create_table()
        return c.fetchall()