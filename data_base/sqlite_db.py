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
        self.range = None
        self.distance = None
        self.time = None
        self.result = None

    def setup(self):
        create = "CREATE TABLE IF NOT EXISTS data (user_id, city, checkin, checkout, quantity, photo, command, range, distance, time, result)"
        self.conn.execute(create)
        self.conn.commit()

    def add_data(self):
        insert = "INSERT INTO data(user_id, city, checkin, checkout, quantity, photo, command, range, distance, time, result) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        self.conn.execute(insert, (self.user_id, self.city, self.checkin,
                                   self.checkout, self.quantity, self.photo,
                                   self.command, self.range, self.distance, 
                                   self.time, self.result))
        self.conn.commit()
    
    
    def add_result(self, result_data, id, user_time):
        update = "UPDATE data SET result = (?) WHERE (user_id = (?)) AND (time = (?))"
        cur = self.conn.cursor()
        cur.execute(update, (result_data, id, user_time))
        self.conn.commit()


    def get_items(self):
        args = (self.id_for_search, )
        select_user_id = "SELECT user_id FROM data WHERE user_id = (?) ORDER BY ROWID DESC LIMIT 1"
        select_city = "SELECT city FROM data WHERE user_id = (?) ORDER BY ROWID DESC LIMIT 1"
        select_checkin = "SELECT checkin FROM data WHERE user_id = (?) ORDER BY ROWID DESC LIMIT 1"
        select_checkout = "SELECT checkout FROM data WHERE user_id = (?) ORDER BY ROWID DESC LIMIT 1"
        select_quantity = "SELECT quantity FROM data WHERE user_id = (?) ORDER BY ROWID DESC LIMIT 1"
        select_photo = "SELECT photo FROM data WHERE user_id = (?) ORDER BY ROWID DESC LIMIT 1"
        select_command = "SELECT command FROM data WHERE user_id = (?) ORDER BY ROWID DESC LIMIT 1"
        select_range = "SELECT range FROM data WHERE user_id = (?) ORDER BY ROWID DESC LIMIT 1"
        select_distance = "SELECT distance FROM data WHERE user_id = (?) ORDER BY ROWID DESC LIMIT 1"
        select_time = "SELECT time FROM data WHERE user_id = (?) ORDER BY ROWID DESC LIMIT 1"
        cur = self.conn.cursor()
        user_id = cur.execute(select_user_id, args).fetchone()[0]
        city = cur.execute(select_city, args).fetchone()[0]
        checkin = cur.execute(select_checkin, args).fetchone()[0]
        checkout = cur.execute(select_checkout, args).fetchone()[0]
        quantity = cur.execute(select_quantity, args).fetchone()[0]
        photo = cur.execute(select_photo, args).fetchone()[0]
        command = cur.execute(select_command, args).fetchone()[0]
        range = cur.execute(select_range, args).fetchone()[0]
        distance = cur.execute(select_distance, args).fetchone()[0]
        time = cur.execute(select_time, args).fetchone()[0]
        return user_id, city, checkin, checkout, quantity, photo, command, range, distance, time


    def fetch_history_data(self):
        args = (self.id_for_search, )
        select_data = "SELECT * FROM data WHERE user_id = (?)"
        cur = self.conn.cursor()
        for item in cur.execute(select_data, args).fetchall():
            yield (item[1], item[2], item[3],
                   item[4], item[5], item[6],
                   item[7], item[8], item[9],
                   item[10])


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
    range = user.get_range()
    distance = user.get_distance()
    time = user.get_time()
    db.user_id = user_id
    db.city = city
    db.checkin = checkin
    db.checkout = checkout
    db.quantity = quantity
    db.photo = photo
    db.command = command
    db.range = range
    db.distance = distance
    db.time = time
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
    user_id, city, checkin, checkout, quantity, photo, command, range, distance, time = db.get_items()
    one_data = (user_id, city, checkin, checkout, quantity, photo, command, range, distance, time)
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


def fetch_sqlite_bestdeal(id):
    """Возвращает последние записанные данные (все, кроме комманды пользователя)

    Returns:
        (str): переменные: city(город), checkin (дата въезда),
        checkout(дата окончания брони), quantity(количество отелей),
        photo(количесто фотографий)
    """
    data = fetch_all_data(id)
    return data[1], data[4], data[5], data[7], data[8]


def fetch_quantities_from_sqlite(id):
    """Возвращает введенные пользователем количество отелей и фотографий

    Returns:
        (int): две переменные: ко-во отелей и кол-во фотографий
    """
    data = fetch_all_data(id)
    return data[4], data[5]


def fetch_history(id):
    db = DBHelper(id)
    db.setup()
    result = list(db.fetch_history_data())
    return result
