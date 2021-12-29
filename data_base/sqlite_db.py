import sqlite3

class DBHelper:
    def __init__(self, dbname="database.db"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)
        self.cur = self.conn.cursor
        self.city = None
        self.checkin = None
        self.checkout = None
        self.quantity = None
        self.photo = None

    def setup(self):
        create = "CREATE TABLE IF NOT EXISTS data (city, checkin, checkout, quantity, photo)"
        self.conn.execute(create)
        self.conn.commit()

    def add_data(self):
        insert = "INSERT INTO data(city, checkin, checkout, quantity, photo) VALUES (?, ?, ?, ?, ?)"
        self.conn.execute(insert, (self.city, self.checkin,
                                   self.checkout, self.quantity, self.photo))
        self.conn.commit()

    # def delete_item(self, item_text):
    #     delete = "DELETE FROM items WHERE description = (?)"
    #     args = (item_text, )
    #     self.conn.execute(delete, args)
    #     self.conn.commit()
    #
    def get_items(self):
        select_city = "SELECT city FROM data ORDER BY ROWID DESC LIMIT 1"
        select_checkin = "SELECT checkin FROM data ORDER BY ROWID DESC LIMIT 1"
        select_checkout = "SELECT checkout FROM data ORDER BY ROWID DESC LIMIT 1"
        select_quantity = "SELECT quantity FROM data ORDER BY ROWID DESC LIMIT 1"
        select_photo = "SELECT photo FROM data ORDER BY ROWID DESC LIMIT 1"
        cur = self.conn.cursor()
        city = cur.execute(select_city).fetchone()[0]
        checkin = cur.execute(select_checkin).fetchone()[0]
        checkout = cur.execute(select_checkout).fetchone()[0]
        quantity = cur.execute(select_quantity).fetchone()[0]
        photo = cur.execute(select_photo).fetchone()[0]
        return city, checkin, checkout, quantity, photo
