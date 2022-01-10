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
        self.command = None

    def setup(self):
        create = "CREATE TABLE IF NOT EXISTS data (city, checkin, checkout, quantity, photo, command)"
        self.conn.execute(create)
        self.conn.commit()

    def add_data(self):
        insert = "INSERT INTO data(city, checkin, checkout, quantity, photo, command) VALUES (?, ?, ?, ?, ?, ?)"
        self.conn.execute(insert, (self.city, self.checkin,
                                   self.checkout, self.quantity, self.photo, self.command))
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
        select_command = "SELECT command FROM data ORDER BY ROWID DESC LIMIT 1"
        cur = self.conn.cursor()
        city = cur.execute(select_city).fetchone()[0]
        checkin = cur.execute(select_checkin).fetchone()[0]
        checkout = cur.execute(select_checkout).fetchone()[0]
        quantity = cur.execute(select_quantity).fetchone()[0]
        photo = cur.execute(select_photo).fetchone()[0]
        command = cur.execute(select_command).fetchone()[0]
        return city, checkin, checkout, quantity, photo, command


def fetch_all_data():
    """Возвращает последние записанные данные из библиотеки sqlite

    Returns:
        (str): переменные: city(город), checkin (дата въезда),
        checkout(дата окончания брони), quantity(количество отелей),
        photo(количесто фотографий), command(какая команда была введена пользователем)
    """
    db = DBHelper()
    db.setup()
    city, checkin, checkout, quantity, photo, command = db.get_items()
    one_data = (city, checkin, checkout, quantity, photo, command)
    return one_data


def fetch_sqlite_data():
    """Возвращает последние записанные данные (все, кроме комманды пользователя)

    Returns:
        (str): переменные: city(город), checkin (дата въезда),
        checkout(дата окончания брони), quantity(количество отелей),
        photo(количесто фотографий)
    """
    data = fetch_all_data()
    return data[0], data[1], data[2], data[3], data[4]


def fetch_quantities_from_sqlite():
    """Возвращает введенные пользователем количество отелей и фотографий

    Returns:
        (int): две переменные: ко-во отелей и кол-во фотографий
    """
    data = fetch_all_data()
    return data[3], data[4]


def fetch_user_command():
    """Возвращает введенную пользователем комманду

    Returns:
        (str): команда пользователя
    """
    data = fetch_all_data()
    return data[5]
