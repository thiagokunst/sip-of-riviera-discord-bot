import json
from models.connection import rpg_db


# Lista todos os usuários
def fetch_all_users():
    try:
        query_cursor = rpg_db.cursor(buffered=True)

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
        query_cursor = rpg_db.cursor(buffered=True)

        query = "SELECT * FROM tb_users WHERE discord_id = %(discord_id)s"
        query_params = {'discord_id': discord_id}
        query_cursor.execute(query, query_params)

        columns = query_cursor.description
        result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                  query_cursor.fetchall()]

        return {"status": True, "data": result}

    except Exception as e:
        print(e)
        return {"status": False, "data": "fetch_user_by_id error"}


# Lista todos os personagens
def fetch_all_characters():
    try:
        query_cursor = rpg_db.cursor(buffered=True)

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
        query_cursor = rpg_db.cursor(buffered=True)

        query = "SELECT tb_characters.*, tb_users.discord_id FROM tb_characters INNER JOIN tb_users ON tb_users.id = " \
                "tb_characters.user_id WHERE tb_users.discord_id = %(discord_id)s"
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

        query = "SELECT tb_users.*, COUNT(DISTINCT(tb_characters.id)) AS char_count FROM tb_users LEFT JOIN " \
                "tb_characters ON tb_users.id = tb_characters.user_id WHERE discord_id = %(discord_id)s GROUP BY " \
                "tb_users.id "
        query_params = {'discord_id': discord_id}
        query_cursor.execute(query, query_params)

        columns = query_cursor.description
        result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                  query_cursor.fetchall()]

        if len(result) == 0:
            query = "INSERT INTO tb_users (discord_id) VALUES (%(discord_id)s)"
            query_params = {'discord_id': discord_id}
            query_cursor.execute(query, query_params)
            rpg_db.commit()
            user_id = query_cursor.lastrowid
        else:
            user_id = result[0]['id']
            if (result[0]['char_count'] > 0 and result[0]['patreon'] == 0) or (
                    result[0]['char_count'] >= 6 and result[0]['patreon'] == 1):
                # return {"status": False, "data": "Você já atingiu o limite máximo de personagens (1 para não
                # apoiadores ou 6 para apoiadores)"}
                return {"status": False, "data": "char_register_limit"}

        query = "INSERT INTO tb_characters (user_id, name, roles_id) VALUES (%(user_id)s, %(name)s, %(roles)s)"
        query_params = {'user_id': user_id, 'name': name, 'roles': json.dumps(roles)}
        query_cursor.execute(query, query_params)
        rpg_db.commit()
        character_id = query_cursor.lastrowid

        query = "UPDATE tb_users SET active_char = %(character_id)s WHERE id = %(user_id)s"
        query_params = {'character_id': character_id, 'user_id': user_id}
        query_cursor.execute(query, query_params)
        rpg_db.commit()

        # return {"status": True, "data": "Personagem cadastrado"}
        return {"status": True, "data": "char_register_success"}

    except Exception as e:
        print(e)
        default_message = "deu erro carai"
        if e.args[0] == 1062:
            # default_message = "Este nome já existe"
            default_message = "char_register_duplicate_name"
        return {"status": False, "data": default_message}


def fetch_character_by_id(character_id):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

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
        query_cursor = rpg_db.cursor(buffered=True)
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
        query_cursor = rpg_db.cursor(buffered=True)
        query = "UPDATE tb_characters SET hero_link = %(hero_link)s WHERE id = (SELECT active_char from tb_users " \
                "WHERE discord_id = %(discord_id)s) "
        query_params = {'hero_link': hero_link, 'discord_id': discord_id}
        query_cursor.execute(query, query_params)
        rpg_db.commit()

        # return {"status": True, "data": "Link salvo"}
        return {"status": True, "data": "char_hfimport_success"}
    except Exception as e:
        print(e)
        default_message = "deu erro carai"
        if e.args[0] == 1062:
            default_message = "char_hfimport_duplicate_link"
        return {"status": False, "data": default_message}


def insert_beyond_link(discord_id, beyond_link):
    try:
        query_cursor = rpg_db.cursor(buffered=True)
        query = "UPDATE tb_characters SET beyond_link = %(beyond_link)s WHERE id = (SELECT active_char from tb_users " \
                "WHERE discord_id = %(discord_id)s) "
        query_params = {'beyond_link': beyond_link, 'discord_id': discord_id}
        query_cursor.execute(query, query_params)
        rpg_db.commit()

        # return {"status": True, "data": "Link salvo"}
        return {"status": True, "data": "char_dndbimport_success"}
    except Exception as e:
        print(e)
        default_message = "deu erro carai"
        if e.args[0] == 1062:
            default_message = "char_dndbimport_duplicate_link"
        return {"status": False, "data": default_message}


def check_if_is_patreon(discord_id):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        query = "SELECT patreon from tb_users WHERE discord_id = %(discord_id)s"
        query_params = {'discord_id': discord_id}
        query_cursor.execute(query, query_params)
        result = query_cursor.fetchall()
        if len(result) == 0:
            return {"status": False, "data": "Usuário não encontrado"}

        return {"status": True, "data": result[0][0]}
    except Exception as e:
        print(e)
        return {"status": False, "data": "deu erro carai"}


def update_patreon(discord_id, patreon_status):
    try:
        query_cursor = rpg_db.cursor(buffered=True)
        query = "UPDATE tb_users SET patreon = %(patreon_status)s WHERE discord_id = %(discord_id)s"
        query_params = {'discord_id': discord_id, 'patreon_status': patreon_status}
        query_cursor.execute(query, query_params)
        rpg_db.commit()

        return {"status": True, "data": "Patreon atualizado"}
    except Exception as e:
        print(e)
        return {"status": False, "data": "deu erro carai"}


def fetch_all_info_messages():
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        query_cursor.execute(
            "SELECT * from tb_messages")

        columns = query_cursor.description
        result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                  query_cursor.fetchall()]

        filtered_result = {}
        for message in result:
            filtered_result[message['message_code']] = message['message']
        return {"status": True, "data": filtered_result}
    except Exception as e:
        print(e)
        return {"status": False, "data": "deu erro carai"}


def insert_master(discord_id):
    try:
        query_cursor = rpg_db.cursor(buffered=True)
        query = "INSERT INTO tb_masters (discord_id) VALUES (%(discord_id)s)"
        query_params = {'discord_id': discord_id}
        query_cursor.execute(query, query_params)
        rpg_db.commit()
        return {"status": True, "data": "mestre inserido"}

    except Exception as e:
        print(e)
        default_message = "deu erro carai"
        if e.args[0] == 1062:
            default_message = "mestre ja existe"
        return {"status": False, "data": default_message}


def insert_mission(discord_id, name):
    try:
        query_cursor = rpg_db.cursor(buffered=True)
        query = "SELECT id FROM tb_users WHERE discord_id = %(discord_id)s"
        query_params = {'discord_id': discord_id}
        query_cursor.execute(query, query_params)
        owner_id = query_cursor.fetchone()[0]

        query = "INSERT INTO tb_missions (owner_id, name) VALUES (%(owner_id)s, %(name)s)"
        query_params = {'owner_id': owner_id, 'name': name}
        query_cursor.execute(query, query_params)
        rpg_db.commit()
        return {"status": True, "data": "missao inserida"}

    except Exception as e:
        print(e)
        default_message = "deu erro carai"
        # if (e.args[0] == 1062):
        #    default_message = "mestre ja existe"
        return {"status": False, "data": default_message}


def insert_party(discord_id, name):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        user_data = fetch_user_by_id(discord_id)['data'][0]
        current_party = user_data['current_party']
        if current_party is not None:
            return {"status": False, "data": "já está em uma party"}
        owner_character_id = user_data['active_char']
        members_json = json.dumps({owner_character_id: discord_id})

        query = "INSERT INTO tb_parties (owner_id, name, members) VALUES (%(owner_character_id)s, %(name)s, " \
                "%(members)s) "
        query_params = {'owner_character_id': owner_character_id, 'name': name, 'members': members_json}
        query_cursor.execute(query, query_params)
        rpg_db.commit()
        party_id = query_cursor.lastrowid

        query = "UPDATE tb_users SET current_party = %(party_id)s WHERE discord_id = %(discord_id)s"
        query_params = {'party_id': party_id, 'discord_id': discord_id}
        query_cursor.execute(query, query_params)
        rpg_db.commit()

        return {"status": True, "data": "party criada"}

    except Exception as e:
        print(e)
        default_message = "insert_party"
        # if (e.args[0] == 1062):
        #    default_message = "mestre ja existe"
        return {"status": False, "data": default_message}


def fetch_party_by_id(party_id):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        query = "SELECT * FROM tb_parties WHERE id = %(party_id)s"
        query_params = {'party_id': party_id}
        query_cursor.execute(query, query_params)
        rpg_db.commit()

        columns = query_cursor.description
        result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                  query_cursor.fetchall()]

        return {"status": True, "data": result}

    except Exception as e:
        print(e)
        default_message = "fetch_party_by_id error"
        return {"status": False, "data": default_message}



def null_current_party_by_discord_id(discord_id):
    try:
        query_cursor = rpg_db.cursor(buffered=True)
        if len(discord_id) > 1:
            query = "UPDATE tb_users SET current_party = %(current_party)s WHERE discord_id IN {}".format(discord_id)
            query_params = {'current_party': None}
            query_cursor.execute(query, query_params)
            rpg_db.commit()
            return {"status": True, "data": "current_party modificado para null"}
        else:
            query = "UPDATE tb_users SET current_party = %(current_party)s WHERE discord_id = %(discord_id)s"
            query_params = {'current_party': None, 'discord_id': discord_id[0]}
            query_cursor.execute(query, query_params)
            rpg_db.commit()
            return {"status": True, "data": "current_party modificado para null"}

    except Exception as e:
        print(e)
        default_message = "null_current_party_by_discord_id error"
        return {"status": False, "data": default_message}


def disband_party(discord_id):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        user_data = fetch_user_by_id(discord_id)['data'][0]
        current_party = user_data['current_party']
        party_data = fetch_party_by_id(current_party)['data'][0]
        members_json = json.loads(party_data['members'])
        members_discord_id_list = []
        for member in members_json.values():
            members_discord_id_list.append(member)
        members_discord_id_tuple = tuple(members_discord_id_list)

        null_current_party_by_discord_id(members_discord_id_tuple)

        query = "DELETE FROM tb_parties WHERE id = %(current_party)s"
        query_params = {'current_party': current_party}
        query_cursor.execute(query, query_params)
        rpg_db.commit()

        return {"status": True, "data": "party desfeita"}

    except Exception as e:
        print(e)
        default_message = "disband_party error"
        return {"status": False, "data": default_message}


def remove_party_member(discord_id):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        user_data = fetch_user_by_id(discord_id)['data'][0]
        current_party = user_data['current_party']
        party_data = fetch_party_by_id(current_party)['data'][0]
        user_character_id = user_data['active_char']
        members_dic = json.loads(party_data['members'])
        members_dic.pop(str(user_character_id))
        members_json = json.dumps(members_dic)

        query = "UPDATE tb_parties SET members = %(members)s WHERE id = %(current_party)s"
        query_params = {'members': members_json, 'current_party': current_party}
        query_cursor.execute(query, query_params)
        rpg_db.commit()

        list_discord_id = [discord_id]
        null_current_party_by_discord_id(list_discord_id)

        return {"status": True, "data": "removido da party"}

    except Exception as e:
        print(e)
        default_message = "fetch_party_by_id error"
        return {"status": False, "data": default_message}


def leave_party(discord_id):
    try:
        user_data = fetch_user_by_id(discord_id)['data'][0]
        current_party = user_data['current_party']
        if current_party is None:
            return {"status": False, "data": "não está em uma party"}

        party_data = fetch_party_by_id(current_party)['data'][0]
        user_character_id = user_data['active_char']
        if party_data['owner_id'] == user_character_id:
            return disband_party(discord_id)
        else:
            return remove_party_member(discord_id)

    except Exception as e:
        print(e)
        default_message = "leave_party error"
        return {"status": False, "data": default_message}


def fetch_user_by_char_name(char_name):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        query = "SELECT user_id FROM tb_characters WHERE name = %(char_name)s"
        query_params = {'char_name': char_name}
        query_cursor.execute(query, query_params)
        rpg_db.commit()
        user_id = query_cursor.fetchone()[0]

        query = "SELECT discord_id FROM tb_users WHERE id = %(user_id)s"
        query_params = {'user_id': user_id}
        query_cursor.execute(query, query_params)
        rpg_db.commit()
        discord_id = query_cursor.fetchone()[0]

        user_data = fetch_user_by_id(discord_id)['data'][0]

        return {"status": True, "data": user_data}

    except Exception as e:
        print(e)
        default_message = "fetch_by_char_name error"
        return {"status": False, "data": default_message}


def join_party(inviter_discord_id, invited_player_discord_id):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        inviter_data = fetch_user_by_id(inviter_discord_id)['data'][0]
        invited_player_data = fetch_user_by_id(invited_player_discord_id)['data'][0]
        if inviter_data['current_party'] is None:
            return {"status": False, "data": "não está numa party"}
        if invited_player_data['current_party'] is not None:
            return {"status": False, "data": "já está numa party"}
        party = fetch_party_by_id(inviter_data['current_party'])['data'][0]
        party_id = party['id']
        members_dic = json.loads(party['members'])
        members_dic[invited_player_data['active_char']] = invited_player_discord_id
        members_json = json.dumps(members_dic)

        query = "UPDATE tb_parties SET members = %(members)s WHERE id = %(party_id)s"
        query_params = {'members': members_json, 'party_id': party_id}
        query_cursor.execute(query, query_params)
        rpg_db.commit()

        query = "UPDATE tb_users SET current_party = %(current_party)s WHERE discord_id IN(%(discord_id)s)"
        query_params = {'current_party': party_id, 'discord_id': invited_player_discord_id}
        query_cursor.execute(query, query_params)
        rpg_db.commit()

        return {"status": True, "data": "entrada bem sucedida"}

    except Exception as e:
        print(e)
        default_message = "join_party error"
        return {"status": False, "data": default_message}
