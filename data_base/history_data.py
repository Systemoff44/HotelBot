from typing import Dict


class History:
    """
        Класс История для создания словаря, в котором
        хранятся данные, полученные из истории 
    """
    users: Dict = dict()

    def __init__(self, chat_id: int) -> None:
        self.user_id = chat_id
        self.all_data = None
        History.add_user(chat_id, self)

    @classmethod
    def add_user(cls, user_id, user):
        cls.users[user_id] = user

    @classmethod
    def get_user(cls, user_id):
        if user_id not in cls.users:
            user = History(user_id)
            cls.users[user_id] = user
            return user
        else:
            return cls.users[user_id]

    def create_all_data(self, data):
        self.all_data = data

    def get_all_data(self):
        return self.all_data
