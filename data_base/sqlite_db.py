import sqlite3


def sql_start():
    global base, cur
    base = sqlite3.connect("users_data.db")
    cur = base.cursor()
    if base:
        print("Data base connected")
    base.execute("CREATE TABLE IF NOT EXISTS data(city, quantity, photo)")
    base.commit()


async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute("INSERT INTO data VALUES (?, ?, ?)", tuple(data.values()))
        base.commit()


async def sql_receive(message):
    for response in cur.execute("SELECT * FROM data").fetchall():
        return message.from_user.id, response[0], f"{response[1]}"

