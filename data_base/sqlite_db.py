import sqlite3
from data_base import user_data


class DBHelper:
    """Класс сбора данных пользователя, записи их в бд, а также
       извлечения необходимых данных из бд
    """
    def __init__(self, id_for_search=None, dbname="database.db"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)
        self.cur = self.conn.cursor
        self.id_for_search = id_for_search
        self.user_id = None
        self.city = None
        self.checkin = None
        self.checkout = None
        self.quantity = None
        self.photo = None
        self.command = None

    def setup(self):
        create = "CREATE TABLE IF NOT EXISTS data (user_id, city, checkin, checkout, quantity, photo, command)"
        self.conn.execute(create)
        self.conn.commit()

    def add_data(self):
        insert = "INSERT INTO data(user_id, city, checkin, checkout, quantity, photo, command) VALUES (?, ?, ?, ?, ?, ?, ?)"
        self.conn.execute(insert, (self.user_id, self.city, self.checkin,
                                   self.checkout, self.quantity, self.photo, self.command))
        self.conn.commit()

    # def delete_item(self, item_text):
    #     delete = "DELETE FROM items WHERE description = (?)"
    #     args = (item_text, )
    #     self.conn.execute(delete, args)
    #     self.conn.commit()
    #
    def get_items(self):
        args = (self.id_for_search, )
        select_user_id = "SELECT user_id FROM data WHERE user_id = (?) ORDER BY ROWID DESC LIMIT 1"
        select_city = "SELECT city FROM data WHERE user_id = (?) ORDER BY ROWID DESC LIMIT 1"
        select_checkin = "SELECT checkin FROM data WHERE user_id = (?) ORDER BY ROWID DESC LIMIT 1"
        select_checkout = "SELECT checkout FROM data WHERE user_id = (?) ORDER BY ROWID DESC LIMIT 1"
        select_quantity = "SELECT quantity FROM data WHERE user_id = (?) ORDER BY ROWID DESC LIMIT 1"
        select_photo = "SELECT photo FROM data WHERE user_id = (?) ORDER BY ROWID DESC LIMIT 1"
        select_command = "SELECT command FROM data WHERE user_id = (?) ORDER BY ROWID DESC LIMIT 1"
        cur = self.conn.cursor()
        user_id = cur.execute(select_user_id, args).fetchone()[0]
        city = cur.execute(select_city, args).fetchone()[0]
        checkin = cur.execute(select_checkin, args).fetchone()[0]
        checkout = cur.execute(select_checkout, args).fetchone()[0]
        quantity = cur.execute(select_quantity, args).fetchone()[0]
        photo = cur.execute(select_photo, args).fetchone()[0]
        command = cur.execute(select_command, args).fetchone()[0]
        return user_id, city, checkin, checkout, quantity, photo, command


def create_request(id):
    db = DBHelper()
    db.setup()
    user = user_data.User.get_user(id)
    user_id = user.get_id()
    city = user.get_city()
    checkin = user.get_checkin()
    checkout = user.get_checkout()
    quantity = user.get_quantity()
    photo = user.get_photo()
    command = user.get_command()
    db.user_id = user_id
    db.city = city
    db.checkin = checkin
    db.checkout = checkout
    db.quantity = quantity
    db.photo = photo
    db.command = command
    db.add_data()


def fetch_all_data(id):
    """Возвращает последние записанные данные из библиотеки sqlite

    Returns:
        (str): переменные: city(город), checkin (дата въезда),
        checkout(дата окончания брони), quantity(количество отелей),
        photo(количесто фотографий), command(какая команда была введена пользователем)
    """
    db = DBHelper(id)
    db.setup()
    user_id, city, checkin, checkout, quantity, photo, command = db.get_items()
    one_data = (user_id, city, checkin, checkout, quantity, photo, command)
    return one_data


def fetch_sqlite_data(id):
    """Возвращает последние записанные данные (все, кроме комманды пользователя)

    Returns:
        (str): переменные: city(город), checkin (дата въезда),
        checkout(дата окончания брони), quantity(количество отелей),
        photo(количесто фотографий)
    """
    data = fetch_all_data(id)
    return data[1], data[2], data[3], data[4], data[5]


def fetch_quantities_from_sqlite(id):
    """Возвращает введенные пользователем количество отелей и фотографий

    Returns:
        (int): две переменные: ко-во отелей и кол-во фотографий
    """
    data = fetch_all_data(id)
    return data[4], data[5]
