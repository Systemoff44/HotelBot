import sqlite3


class DBHelper:
    def __init__(self, dbname="database.db"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)
        self.cur = self.conn.cursor
        self.city = None
        self.quantity = None
        self.photo = None

    def setup(self):
        create = "CREATE TABLE IF NOT EXISTS data (city, quantity, photo)"
        self.conn.execute(create)
        self.conn.commit()

    def add_data(self):
        insert = "INSERT INTO data(city, quantity, photo) VALUES (?, ?, ?)"
        self.conn.execute(insert, (self.city, self.quantity, self.photo))
        self.conn.commit()

    # def delete_item(self, item_text):
    #     delete = "DELETE FROM items WHERE description = (?)"
    #     args = (item_text, )
    #     self.conn.execute(delete, args)
    #     self.conn.commit()
    #
    def get_items(self):
        select = "SELECT city FROM data ORDER BY ROWID DESC LIMIT 1"
        cur = self.conn.cursor()
        return cur.execute(select).fetchone()[0]
