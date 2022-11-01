from models.connection import rpg_db


def fetch_all_users():
    try:
        query_cursor = rpg_db.cursor()

        query_cursor.execute(
            "SELECT tb_users.*, COUNT(DISTINCT(tb_characters.id)) AS char_count FROM tb_users INNER JOIN "
            "tb_characters ON tb_characters.user_id = tb_users.id GROUP BY tb_users.id")

        columns = query_cursor.description
        result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                  query_cursor.fetchall()]

        return {"status": True, "data": result}
    except Exception as e:
        print(e)
        return {"status": False, "data": "deu erro carai"}

def fetch_user_by_id(discord_id):
    try:
        query_cursor = rpg_db.cursor()

        query = "SELECT * FROM tb_users WHERE discord_id = %(discord_id)s"
        query_params = {'discord_id': discord_id}
        query_cursor.execute(query, query_params)

        columns = query_cursor.description
        result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                  query_cursor.fetchall()]

        return {"status": True, "data": result}
    except Exception as e:
        print(e)
        return {"status": False, "data": "deu erro carai"}

def insert_user(discord_id):
    try:
        query_cursor = rpg_db.cursor()

        query = "INSERT INTO tb_users (discord_id) VALUES (%(discord_id)s)"
        query_params = {'discord_id': discord_id}
        query_cursor.execute(query, query_params)

        rpg_db.commit()

        return {"status": True, "data": query_cursor.lastrowid}
    except Exception as e:
        print(e)
        return {"status": False, "data": "deu erro carai"}

def insert_character(user_id, name):
    try:
        query_cursor = rpg_db.cursor()

        query = "INSERT INTO tb_characters (user_id, name) VALUES (%(user_id)s, %(name)s)"
        query_params = {'user_id': user_id, 'name': name}
        query_cursor.execute(query, query_params)

        rpg_db.commit()

        return {"status": True, "data": query_cursor.lastrowid}
    except Exception as e:
        default_message = "deu erro carai"
        if(e.args[0] == 1062):
            default_message = "Este nome já existe"

        return {"status": False, "data": default_message}

def fetch_all_characters():
    try:
        query_cursor = rpg_db.cursor()

        query_cursor.execute(
            "SELECT tb_characters.*, tb_users.discord_id FROM tb_characters INNER JOIN tb_users ON tb_users.id = "
            "tb_characters.user_id")

        columns = query_cursor.description
        result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                  query_cursor.fetchall()]

        return {"status": True, "data": result}
    except Exception as e:
        print(e)
        return {"status": False, "data": "deu erro carai"}


def fetch_all_characters_by_id(discord_id):
    try:
        query_cursor = rpg_db.cursor()

        query = "SELECT tb_characters.*, tb_users.discord_id FROM tb_characters INNER JOIN tb_users ON tb_users.id = tb_characters.user_id WHERE tb_users.discord_id = %(discord_id)s"
        query_params = {'discord_id': discord_id}
        query_cursor.execute(query, query_params)

        columns = query_cursor.description
        result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                  query_cursor.fetchall()]

        return {"status": True, "data": result}
    except Exception as e:
        print(e)
        return {"status": False, "data": "deu erro carai"}
