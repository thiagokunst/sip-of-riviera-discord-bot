from models.connection import rpg_db

# Lista todos os usuários
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

# Lista usuário por discord_id
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

# Lista todos os personagens
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

# Lista todos os personagens de um usuário buscando por discord_id
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


# Insere o usuário (caso ainda não esteja cadastrado) e insere o personagem
def insert_user_and_character(discord_id, name):
    try:
        query_cursor = rpg_db.cursor()

        query = "SELECT * FROM tb_users WHERE discord_id = %(discord_id)s"
        query_params = {'discord_id': discord_id}
        query_cursor.execute(query, query_params)

        columns = query_cursor.description
        result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                  query_cursor.fetchall()]

        if(len(result) == 0):
            query = "INSERT INTO tb_users (discord_id) VALUES (%(discord_id)s)"
            query_params = {'discord_id': discord_id}
            query_cursor.execute(query, query_params)
            rpg_db.commit()
            user_id = query_cursor.lastrowid
        else:
            user_id = result[0]['id']

        query = "INSERT INTO tb_characters (user_id, name) VALUES (%(user_id)s, %(name)s)"
        query_params = {'user_id': user_id, 'name': name}
        query_cursor.execute(query, query_params)
        rpg_db.commit()

        return {"status": True, "data": "Personagem cadastrado"}

    except Exception as e:
        print(e)
        default_message = "deu erro carai"
        if (e.args[0] == 1062):
            default_message = "Este nome já existe"
        return {"status": False, "data": default_message}
