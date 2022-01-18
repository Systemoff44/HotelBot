class User:
    """Класс юзер, для получения и сбора промежуточных данных"""
    
    users = dict()

    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.command = None
        self.city = None
        self.checkin = None
        self.checkout = None
        self.quantity = None
        self.photo = None
        User.add_user(chat_id, self)

    @classmethod
    def add_user(cls, chat_id, user):
        cls.users[chat_id] = user

    @classmethod
    def get_user(cls, user_id):
        if user_id not in cls.users:
            user = User(user_id)
            cls.users[user_id] = user
            return user
        else:
            return cls.users[user_id]

    def get_id(self):
        return self.chat_id

    def create_command(self, command):
        self.command = command

    def create_city(self, city):
        self.city = city

    def create_checkin(self, checkin):
        self.checkin = checkin

    def create_checkout(self, checkout):
        self.checkout = checkout

    def create_quantity(self, quantity):
        self.quantity = quantity

    def create_photo(self, photo):
        self.photo = photo

    def get_city(self):
        return self.city

    def get_command(self):
        return self.command

    def get_checkin(self):
        return self.checkin

    def get_checkout(self):
        return self.checkout

    def get_quantity(self):
        return self.quantity

    def get_photo(self):
        return self.photo