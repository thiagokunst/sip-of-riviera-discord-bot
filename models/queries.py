import json
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
def insert_user_and_character(discord_id, name, roles):
    try:
        query_cursor = rpg_db.cursor()

        query = "SELECT tb_users.*, COUNT(DISTINCT(tb_characters.id)) AS char_count FROM tb_users LEFT JOIN tb_characters ON tb_users.id = tb_characters.user_id WHERE discord_id = %(discord_id)s GROUP BY tb_users.id"
        query_params = {'discord_id': discord_id}
        query_cursor.execute(query, query_params)

        columns = query_cursor.description
        result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                  query_cursor.fetchall()]
        if (len(result) == 0):
            query = "INSERT INTO tb_users (discord_id) VALUES (%(discord_id)s)"
            query_params = {'discord_id': discord_id}
            query_cursor.execute(query, query_params)
            rpg_db.commit()
            user_id = query_cursor.lastrowid
        else:
            user_id = result[0]['id']
            if (result[0]['char_count'] > 0 and result[0]['patreon'] == 0) or (
                    result[0]['char_count'] >= 6 and result[0]['patreon'] == 1):
                return {"status": False,
                        "data": "Você já atingiu o limite máximo de personagens (1 para não apoiadores ou 6 para apoiadores)"}

        query = "INSERT INTO tb_characters (user_id, name, roles_id) VALUES (%(user_id)s, %(name)s, %(roles)s)"
        query_params = {'user_id': user_id, 'name': name, 'roles': json.dumps(roles)}
        query_cursor.execute(query, query_params)
        rpg_db.commit()
        character_id = query_cursor.lastrowid

        query = "UPDATE tb_users SET active_char = %(character_id)s WHERE id = %(user_id)s"
        query_params = {'character_id': character_id, 'user_id': user_id}
        query_cursor.execute(query, query_params)
        rpg_db.commit()

        return {"status": True, "data": "Personagem cadastrado"}

    except Exception as e:
        print(e)
        default_message = "deu erro carai"
        if (e.args[0] == 1062):
            default_message = "Este nome já existe"
        return {"status": False, "data": default_message}


def fetch_character_by_id(character_id):
    try:
        query_cursor = rpg_db.cursor()

        query = "SELECT * from tb_characters WHERE id = %(character_id)s"
        query_params = {'character_id': character_id}
        query_cursor.execute(query, query_params)

        columns = query_cursor.description
        result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                  query_cursor.fetchall()]
        return {"status": False, "data": result}
    except Exception as e:
        print(e)
        return {"status": False, "data": "deu erro carai"}


def fetch_character_by_id_and_insert_active_character(character_id):
    try:
        query_cursor = rpg_db.cursor()
        query = "SELECT * from tb_characters WHERE id = %(character_id)s"
        query_params = {'character_id': character_id}
        query_cursor.execute(query, query_params)
        columns = query_cursor.description
        result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                  query_cursor.fetchall()]

        query = "UPDATE tb_users SET active_char = %(character_id)s WHERE id = %(user_id)s"
        query_params = {'character_id': result[0]['id'], 'user_id': result[0]['user_id']}
        query_cursor.execute(query, query_params)
        rpg_db.commit()

        return {"status": True, "data": result}
    except Exception as e:
        print(e)
        return {"status": False, "data": "deu erro carai"}


def insert_hero_link(discord_id, hero_link):
    try:
        query_cursor = rpg_db.cursor()
        query = "UPDATE tb_characters SET hero_link = %(hero_link)s WHERE id = (SELECT active_char from tb_users WHERE discord_id = %(discord_id)s)"
        query_params = {'hero_link': hero_link, 'discord_id': discord_id}
        query_cursor.execute(query, query_params)
        rpg_db.commit()

        return {"status": True, "data": "Link salvo"}
    except Exception as e:
        print(e)
        return {"status": False, "data": "deu erro carai"}


def insert_beyond_link(discord_id, beyond_link):
    try:
        query_cursor = rpg_db.cursor()
        query = "UPDATE tb_characters SET beyond_link = %(beyond_link)s WHERE id = (SELECT active_char from tb_users WHERE discord_id = %(discord_id)s)"
        query_params = {'beyond_link': beyond_link, 'discord_id': discord_id}
        query_cursor.execute(query, query_params)
        rpg_db.commit()

        return {"status": True, "data": "Link salvo"}
    except Exception as e:
        print(e)
        return {"status": False, "data": "deu erro carai"}


def check_if_is_patreon(discord_id):
    try:
        query_cursor = rpg_db.cursor()

        query = "SELECT patreon from tb_users WHERE discord_id = %(discord_id)s"
        query_params = {'discord_id': discord_id}
        query_cursor.execute(query, query_params)
        result = query_cursor.fetchall()
        if(len(result) == 0): return {"status": False, "data": "Usuário não encontrado"}

        return {"status": True, "data": result[0][0]}
    except Exception as e:
        print(e)
        return {"status": False, "data": "deu erro carai"}


def update_patreon(discord_id, patreon_status):
    try:
        query_cursor = rpg_db.cursor()
        query = "UPDATE tb_users SET patreon = %(patreon_status)s WHERE discord_id = %(discord_id)s"
        query_params = {'discord_id': discord_id, 'patreon_status': patreon_status}
        query_cursor.execute(query, query_params)
        rpg_db.commit()

        return {"status": True, "data": "Patreon atualizado"}
    except Exception as e:
        print(e)
        return {"status": False, "data": "deu erro carai"}
