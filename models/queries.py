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
        return {"status": True, "data": "master_register_sucess"}

    except Exception as e:
        print(e)
        default_message = "insert_master error"
        if e.args[0] == 1062:
            default_message = "master_register_duplicate_id"
        return {"status": False, "data": default_message}


def insert_mission(discord_id, channel_id, dificuldade):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        query = "SELECT id FROM tb_masters WHERE discord_id = %(discord_id)s"
        query_params = {'discord_id': discord_id}
        query_cursor.execute(query, query_params)
        owner_id = query_cursor.fetchone()[0]

        query = "INSERT INTO tb_missions (owner_id, channel_id, difficulty) VALUES (%(owner_id)s, %(channel_id)s, %(dificuldade)s)"
        query_params = {'owner_id': owner_id, 'channel_id':channel_id, 'dificuldade': dificuldade}
        query_cursor.execute(query, query_params)
        rpg_db.commit()
        return {"status": True, "data": "mission_register_sucess"}

    except Exception as e:
        print(e)
        default_message = "insert_mission error"
        if (e.args[0] == 1062):
            default_message = "mission_register_duplicate_name"
        return {"status": False, "data": default_message}


def insert_party(discord_id, mission_channel_id):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        user_data = fetch_user_by_id(discord_id)['data'][0]
        owner_character_id = user_data['active_char']
        members_json = json.dumps({owner_character_id: discord_id})

        query = "INSERT INTO tb_parties (owner_id, mission_channel_id, members) VALUES (%(owner_character_id)s, %(mission_channel_id)s, %(members)s)"
        query_params = {'owner_character_id': owner_character_id, 'mission_channel_id': mission_channel_id, 'members': members_json}
        query_cursor.execute(query, query_params)
        rpg_db.commit()
        party_id = query_cursor.lastrowid


        return {"status": True, "data": party_id}

    except Exception as e:
        print(e)
        default_message = "insert_party error"
        if e.args[0] == 1062:
            default_message = "create_party_duplicate"
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


def disband_party(party_id):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        query = f"DELETE FROM tb_parties WHERE id = {party_id}"
        query_cursor.execute(query)
        rpg_db.commit()

        return {"status": True, "data": "party_disband"}

    except Exception as e:
        print(e)
        default_message = "disband_party error"
        return {"status": False, "data": default_message}


def remove_party_member(discord_id, party_id):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        party_data = fetch_party_by_id(party_id)['data'][0]
        members_dic = json.loads(party_data['members'])
        if discord_id not in members_dic.values():
            return {"status": False, "data": "not_in_the_party"}
        new_dic = {key: value for key, value in members_dic.items() if value != discord_id}
        members_json = json.dumps(new_dic)

        query = "UPDATE tb_parties SET members = %(members_json)s WHERE id = %(party_id)s"
        params = {'members_json': members_json, 'party_id': party_id}
        query_cursor.execute(query, params)
        rpg_db.commit()

        return {"status": True, "data": "player_removed"}

    except Exception as e:
        print(e)
        default_message = "fetch_party_by_id error"
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
        default_message = "char_name_not_found"
        return {"status": False, "data": default_message}


def insert_player_in_party(player_discord_id, character_id, party_id):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        party = fetch_party_by_id(party_id)['data'][0]
        members_dic = json.loads(party['members'])
        if str(character_id) in members_dic.keys():
            return {"status": False, "data": "player_already_in_party"}
        members_dic[character_id] = player_discord_id
        members_json = json.dumps(members_dic)

        query = "UPDATE tb_parties SET members = %(members)s WHERE id = %(party_id)s"
        query_params = {'members': members_json, 'party_id': party_id}
        query_cursor.execute(query, query_params)
        rpg_db.commit()

        return {"status": True, "data": members_dic}

    except Exception as e:
        print(e)
        default_message = "insert_player_in_party error"
        return {"status": False, "data": default_message}


def fetch_master_by_discord_id(discord_id):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        query = "SELECT * FROM tb_masters WHERE discord_id = %(discord_id)s"
        query_params = {'discord_id': discord_id}
        query_cursor.execute(query, query_params)
        rpg_db.commit()

        columns = query_cursor.description
        result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                  query_cursor.fetchall()]

        return {"status": True, "data": result}

    except Exception as e:
        print(e)
        default_message = "fetch_master_by_discord_id error"
        return {"status": False, "data": default_message}


def fetch_mission_by_id(mission_id):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        query = "SELECT * FROM tb_missions WHERE id = %(mission_id)s"
        query_params = {'mission_id': mission_id}
        query_cursor.execute(query, query_params)
        rpg_db.commit()

        columns = query_cursor.description
        result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                  query_cursor.fetchall()]

        return {"status": True, "data": result}

    except Exception as e:
        print(e)
        default_message = "fetch_mission_by_id error"
        return {"status": False, "data": default_message}


def gold_edit(characters_id, amount):
    try:
        query_cursor = rpg_db.cursor(buffered=True)
        if len(characters_id) > 1:
            query = "UPDATE tb_characters SET gold = gold + %(amount)s WHERE id IN {}".format(characters_id)
            query_params = {'amount': amount}
            query_cursor.execute(query, query_params)
            rpg_db.commit()
            return {"status": True, "data": "valor de gold alterado"}
        else:
            query = "UPDATE tb_characters SET gold = gold + %(amount)s WHERE id = %(characters_id)s"
            query_params = {'amount': amount, 'characters': characters_id[0]}
            query_cursor.execute(query, query_params)
            rpg_db.commit()
            return {"status": True, "data": "valor de gold alterado"}

    except Exception as e:
        print(e)
        default_message = "gold_edit error"
        return {"status": False, "data": default_message}


def calculate_party_level(members):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        query = "SELECT level FROM tb_characters WHERE id IN {}".format(members)
        query_cursor.execute(query)
        rpg_db.commit()
        result = 0
        for level in query_cursor.fetchall():
            result += level[0]
        party_level = result/len(members)

        return {"status": True, "data": int(party_level)}

    except Exception as e:
        print(e)
        default_message = "calculate_party_level error"
        return {"status": False, "data": default_message}


def fetch_reward_by_level(party_level):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        query = "SELECT * FROM tb_rewards WHERE level = %(party_level)s"
        query_params = {'party_level': party_level}
        query_cursor.execute(query, query_params)

        columns = query_cursor.description
        result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                  query_cursor.fetchall()]

        return {"status": True, "data": result}

    except Exception as e:
        print(e)
        return {"status": False, "data": "fetch_reward_level error"}


def fetch_characters_list_by_id(characters_id):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        query = "SELECT * FROM tb_characters WHERE id IN {}".format(characters_id)
        query_cursor.execute(query)

        columns = query_cursor.description
        result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                  query_cursor.fetchall()]

        return {"status": True, "data": result}

    except Exception as e:
        print(e)
        return {"status": False, "data": "fetch_characters_list_by_id error"}

def fetch_leveling_chart():
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        query = "SELECT level, exp_needed FROM tb_rewards"
        query_cursor.execute(query)

        columns = query_cursor.description
        preresult = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                  query_cursor.fetchall()]

        result = {}
        for dic in preresult:
            result.update({dic['level']: dic['exp_needed']})
        return {"status": True, "data": result}

    except Exception as e:
        print(e)
        return {"status": False, "data": "fetch_leveling_chart error"}


def check_leveling(characters, exp_amount):
    chart = fetch_leveling_chart()['data']
    message_list = []
    tuple_list = []
    for char in characters:
        if char['exp'] + exp_amount >= chart[char['level']]:
            message_list.append("{} upou para o level {}.".format(char['name'], str(char['level']+1)))
            tuple_list.append((char['id'], char['exp']+exp_amount, char['level']+1))
        else:
            tuple_list.append((char['id'], char['exp'] + exp_amount, char['level']))
    return (message_list, tuple_list)


def exp_edit(characters_id, exp_amount):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        if len(characters_id) > 1:
            characters = fetch_characters_list_by_id(characters_id)['data']
            message = check_leveling(characters, exp_amount)[0]
            tuples = check_leveling(characters, exp_amount)[1]
            placeholder = ("{}," * len(characters_id))[:-1]

            prequery = "INSERT INTO tb_characters (id, exp, tb_characters.level) VALUES " + placeholder + " AS char_data ON DUPLICATE KEY UPDATE exp = char_data.exp, tb_characters.level = char_data.level"
            query = prequery.format(*tuples)
            query_cursor.execute(query)
            rpg_db.commit()
            return {"status": True, "data": message}
        else:
            character = fetch_character_by_id(characters_id[0])['data'][0]
            leveling_tuple = check_leveling([character], exp_amount)
            message = leveling_tuple[0]
            tuples = leveling_tuple[1]

            query = "UPDATE tb_characters SET exp = {}, level = {} WHERE id = {}".format(tuples[0][1], tuples[0][2], characters_id[0])
            query_cursor.execute(query)
            rpg_db.commit()
            return {"status": True, "data": message}

    except Exception as e:
        print(e)
        default_message = "exp_edit error"
        return {"status": False, "data": default_message}


def process_mission(channel_id, exp_multiplier, gold_multiplier):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        query = f"SELECT tb_parties.members, tb_missions.difficulty FROM tb_missions INNER JOIN tb_parties ON tb_missions.current_party=tb_parties.id WHERE tb_missions.channel_id = {channel_id}"
        query_cursor.execute(query)
        rpg_db.commit()

        columns = query_cursor.description
        result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                  query_cursor.fetchall()][0]

        members = json.loads(result['members'])
        mission_level = result['difficulty']
        party_level = calculate_party_level(tuple(members.keys()))['data']+mission_level-1
        reward_level = fetch_reward_by_level(party_level)['data'][0]
        gold_amount = reward_level['gold']*gold_multiplier
        gold_edit(tuple(members.keys()), gold_amount)

        exp_amount = reward_level['exp']*exp_multiplier

        exp_result = exp_edit(tuple(members.keys()), exp_amount)['data']

        return {"status": True, "data": exp_result}

    except Exception as e:
        print(e)
        default_message = "process_mission error"
        return {"status": False, "data": default_message}

def mission_sucess(channel_id):
    return process_mission(channel_id, 1, 1)

def mission_failure(channel_id):
    return process_mission(channel_id, 0.5, 0)

def char_info(discord_id):
    user = fetch_user_by_id(discord_id)['data'][0]
    char = fetch_character_by_id(user['active_char'])['data'][0]
    return char['name']

def party_info(discord_id):
    user = fetch_user_by_id(discord_id)['data'][0]
    party = fetch_party_by_id(user['current_party'])['data'][0]
    return party['members']


def fetch_active_char_data_by_discord_id(discord_id, columns_list):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        columns_list_string = ", ".join(columns_list)
        query = f"SELECT {columns_list_string} FROM tb_characters INNER JOIN tb_users ON tb_characters.user_id=tb_users.id WHERE tb_users.discord_id = {discord_id}"
        query_cursor.execute(query)
        rpg_db.commit()

        columns = query_cursor.description
        result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                  query_cursor.fetchall()][0]

        return {"status": True, "data": result}

    except Exception as e:
        print(e)
        default_message = "fetch_active_char_data_by_discord_id error"
        return {"status": False, "data": default_message}


def fetch_host_id_by_party_id(party_id):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        query = f"SELECT discord_id FROM tb_characters INNER JOIN tb_parties ON tb_characters.id=tb_parties.owner_id INNER JOIN tb_users ON tb_characters.user_id=tb_users.id WHERE tb_parties.id = {party_id}"
        query_cursor.execute(query)
        rpg_db.commit()

        columns = query_cursor.description
        result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                  query_cursor.fetchall()][0]

        return {"status": True, "data": result}

    except Exception as e:
        print(e)
        default_message = "fetch_host_id_by_party_id error"
        return {"status": False, "data": default_message}


def fetch_group_hosts_by_channel(channel_id):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        query = f"SELECT tb_characters.name, tb_parties.id FROM tb_characters INNER JOIN tb_parties ON tb_characters.id=tb_parties.owner_id WHERE tb_parties.mission_channel_id = {channel_id}"
        query_cursor.execute(query)
        rpg_db.commit()

        columns = query_cursor.description
        result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                  query_cursor.fetchall()]

        return {"status": True, "data": result}

    except Exception as e:
        print(e)
        default_message = "fetch_host_id_by_party_id error"
        return {"status": False, "data": default_message}


def check_channel_id_owner(master_id):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        query = f"SELECT channel_id FROM tb_missions INNER JOIN tb_masters ON tb_missions.owner_id=tb_masters.id WHERE tb_masters.discord_id = {master_id}"
        query_cursor.execute(query)
        rpg_db.commit()

        columns = query_cursor.description
        result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                  query_cursor.fetchall()][0]

        return {"status": True, "data": result}

    except Exception as e:
        print(e)
        default_message = "fetch_host_id_by_party_id error"
        return {"status": False, "data": default_message}


def change_mission_active_party(mission_channel_id, party_id):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        query = f"UPDATE tb_missions SET current_party = {party_id} WHERE channel_id = {mission_channel_id}"
        query_cursor.execute(query)
        rpg_db.commit()

        return {"status": True, "data": "party_selected"}

    except Exception as e:
        print(e)
        default_message = "fetch_host_id_by_party_id error"
        return {"status": False, "data": default_message}


def fetch_party_by_channel_id(channel_id):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        query = f"SELECT tb_parties.members FROM tb_missions INNER JOIN tb_parties ON tb_missions.current_party=tb_parties.id WHERE tb_missions.channel_id = {channel_id}"
        query_cursor.execute(query)
        rpg_db.commit()

        columns = query_cursor.description
        result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                  query_cursor.fetchall()][0]

        return {"status": True, "data": result}

    except Exception as e:
        print(e)
        default_message = "fetch_host_id_by_party_id error"
        return {"status": False, "data": default_message}


def delete_mission(mission_channel_id):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        query = f"DELETE FROM tb_missions WHERE tb_missions.channel_id = {mission_channel_id}"
        query_cursor.execute(query)
        rpg_db.commit()

        query = f"DELETE FROM tb_parties WHERE tb_parties.mission_channel_id = {mission_channel_id}"
        query_cursor.execute(query)
        rpg_db.commit()

        return {"status": True, "data": "channel_deleted"}

    except Exception as e:
        print(e)
        default_message = "fetch_host_id_by_party_id error"
        return {"status": False, "data": default_message}


def tier_calculator(level):
    if level in [0, 1, 2, 3, 4]:
        return 1
    elif level in [5, 6, 7, 8, 9, 10]:
        return 2
    elif level in [11, 12, 13, 14, 15, 16]:
        return 3
    elif level in [17, 18, 19, 20]:
        return 4
    else:
        return 5


def fetch_items_by_level(level):
    try:
        query_cursor = rpg_db.cursor(buffered=True)

        tier = tier_calculator(level)
        query = f"SELECT tb_trial_items.name FROM tb_trial_items WHERE tb_trial_items.tier = {tier}"
        query_cursor.execute(query)
        rpg_db.commit()

        result = query_cursor.fetchall()
        return {"status": True, "data": result}

    except Exception as e:
        print(e)
        default_message = "fetch_items_by_level error"
        return {"status": False, "data": default_message}