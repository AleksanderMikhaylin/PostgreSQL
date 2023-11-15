import psycopg2


# Функция, создающая структуру БД (таблицы).
def create_tables(conn: object) -> object:
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS clients(
            id SERIAL PRIMARY KEY,
            name VARCHAR(40),
            surname VARCHAR(40),
            email VARCHAR(40)
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS phones(
            phone VARCHAR(12),
            id_client INTEGER NOT NULL REFERENCES clients(id)
        );
        """)
        # conn.commit()

# Функция, позволяющая добавить телефон для существующего клиента.
def add_phone(conn, id_client, phone, messages=True):

    if phone == None:
        return

    with conn.cursor() as cur:

        cur.execute("""
        SELECT id, name, surname FROM clients WHERE id=%s;
        """, (id_client,))

        result = cur.fetchone()
        if not result is None: # id клиента нашли

            name = result[1]
            surname = result[2]

            cur.execute("""
            SELECT phone FROM phones WHERE phone=%s and id_client=%s;
            """, (phone,id_client))

            result = cur.fetchone()
            if result is None: # такого номера телефона у клиента нет, добавляем
                cur.execute("""
                INSERT INTO phones(phone, id_client) VALUES(%s, %s);
                """, (phone, id_client))
                # conn.commit()
                if messages:
                    print()
                    print(f'Клиенту {name} {surname} добавлен телефон: {phone}')
            else:
                if messages:
                    print()
                    print(f'У клиента {name} {surname} телефон {phone} уже добавлен')
        else:
            if messages:
                print()
                print(f'Клиент с id={id_client} не найден!')

# Функция, позволяющая добавить нового клиента.
def add_client(conn, name, surname, email, phone=None, messages=True):

    with conn.cursor() as cur:

        cur.execute("""
        SELECT id FROM clients WHERE name=%s and surname=%s and email=%s;
        """, (name, surname, email))

        result = cur.fetchone()
        if result is None:
            cur.execute("""
            INSERT INTO clients(name, surname, email) VALUES(%s, %s, %s) RETURNING id;
            """, (name, surname, email))
            id_client = cur.fetchone()[0]
            # conn.commit()
            if messages:
                print()
                print(f'Клиент {name} {surname}, email: {email} занесен в БД с id={id_client}')
            add_phone(conn, id_client, phone, messages)
            return id_client
        else:
            if messages:
                print()
                print(f'Клиент с такими комбинациями Имя = {name}, Фамилия = {surname} и email = {email} существует!')
            return result[0]

# Функция, позволяющая изменить данные о клиенте.

def update_clietn(conn, id_client, name=None, surname=None, email=None, messages=True):

        with conn.cursor() as cur:
            if not name == None:
                cur.execute("""
                UPDATE clients SET name=%s WHERE id=%s;
                """, (name, id_client))
            if not surname == None:
                cur.execute("""
                UPDATE clients SET surname=%s WHERE id=%s;
                """, (surname, id_client))
            if not email == None:
                cur.execute("""
                UPDATE clients SET email=%s WHERE id=%s;
                """, (email, id_client))
                # conn.commit()
            if messages:
                print()
                print(f'Данные клиента с id={id_client} обновлены!')

# Функция, позволяющая удалить телефон для существующего клиента.
def del_phone(conn, id_client, phone, messages=True):

    with conn.cursor() as cur:

        cur.execute("""
        SELECT id, name, surname FROM clients WHERE id=%s;
        """, (id_client,))

        result = cur.fetchone()
        if not result is None: # id клиента нашли

            name = result[1]
            surname = result[2]

            cur.execute("""
            SELECT phone FROM phones WHERE phone=%s and id_client=%s;
            """, (phone,id_client))

            result = cur.fetchone()
            if not result is None: # такого номера телефона у клиента нет, добавляем
                cur.execute("""
                DELETE FROM phones WHERE phone=%s and id_client=%s;
                """, (phone, id_client))
                # conn.commit()
                if messages:
                    print()
                    print(f'Телефон {phone} у клиента {name} {surname} удален!')
            else:
                if messages:
                    print()
                    print(f'Телефон {phone} у клиента {name} {surname} не найден!')
        else:
            if messages:
                print()
                print(f'Ошибка удаления номера телефона, клиент с id={id_client} не найден!')

# Функция, позволяющая удалить существующего клиента.
def del_client(conn, id_client, messages=True):

    with conn.cursor() as cur:

        cur.execute("""
        SELECT name, surname, email FROM clients WHERE id=%s;
        """, (id_client,))

        result = cur.fetchone()
        if not result is None: # id клиента нашли

            name = result[0]
            surname = result[1]
            email = result[2]

            cur.execute("""
            DELETE FROM phones WHERE id_client=%s;
            """, (id_client,))

            cur.execute("""
            DELETE FROM clients WHERE id=%s;
            """, (id_client,))
            # conn.commit()
            if messages:
                print()
                print(f'Клиент {name} {surname} с email {email} удален! ')
        else:
            if messages:
                print()
                print(f'Клиент с id={id_client} не найден!')

# # Функция проверяет, существует ли id клиента в таблице
def id_client_is_valid(id_client):
    find = False
    if id_client is None:
        pass
    elif not type(id_client) == int:
        pass
    else:
        with conn.cursor() as cur:

            cur.execute("""
            SELECT id FROM clients WHERE id=%s;
            """, (id_client,))

            result = cur.fetchone()
            find = not result is None

    if not find:
        print()
        print(f'Клиент с id={id_client} не найден!')

    return find

# # Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону.
def find_client(conn, name=None, surname=None, email=None, phone=None) -> list:

    client_list = []
    with conn.cursor() as cur:

        all_name = name == None
        all_surname = surname == None
        all_email = email == None
        all_phone = phone == None

        cur.execute("""
        SELECT c.id, c.name, c.surname, c.email, p.phone 
        FROM clients as c 
            left join phones p
                on c.id = p.id_client
        WHERE (c.name iLIKE %s or True=%s) 
            and (c.surname iLIKE %s or True=%s)
            and (c.email iLIKE %s or True=%s)
            and (p.phone iLIKE %s or True=%s);
        """, ('%'+name+'%', all_name, '%'+surname+'%', all_surname, '%'+email+'%', all_email, '%'+phone+'%', all_phone))

        result = cur.fetchall()
        client_list += result

    return list(set(client_list))

# # Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону.
def all_client(conn) -> list:

    client_list = []
    with conn.cursor() as cur:

        cur.execute("""
        SELECT c.id, c.name, c.surname, c.email, p.phone FROM clients c
            left join phones p
                on c.id = p.id_client;
        """)
        client_list = cur.fetchall()

    return client_list

def clear_all_phones(conn, messages=True):

    with conn.cursor() as cur:

        cur.execute("""
        DELETE FROM phones
        """)
        # conn.commit()
        if messages:
            print()
            print(f'Таблица телефонов очищена')

def clear_all_client(conn, messages=True):

    # clear_all_phones(False)
    with conn.cursor() as cur:

        cur.execute("""
        SELECT * FROM phones;
        """)
        result = cur.fetchall()

        if len(result) == 0:
            cur.execute("""
            DELETE FROM clients
            """)
            # conn.commit()
            if messages:
                print()
                print(f'Таблица клиентов очищена')
        else:
            if messages:
                print()
                print(f'Ошибка очистки таблицы клиентов')

def input_id_clietn():
    id_client = ''
    id = input('Введите id клиента (целое число): ')

    for i in id:
        if not i in ['0','1','2','3','4','5','6','7','8','9']:
            break
        id_client += i

    if id_client == id:
        return int(id_client)

    return id

def input_key():
    key = input('0 - Выход\n'
                '1 - Добавить клиента\n'
                '2 - Добавить телефон клиента\n'
                '3 - Изменить данные клиента\n'
                '4 - Удалить телефон клиента\n'
                '5 - Удалить клиента\n'
                '6 - Найти клиента\n'
                '7 - Вывести список всех клиентов\n'
                '8 - Удалить все телефоны клиентов\n'
                '9 - Удалить всех клиентов\n'
                'Ваш выбор: ')
    return key


if __name__ == '__main__':

    data_base = input('Введите имя БД>: ')
    user = input('Введите логин: ')
    password = input('Введите пароль: ')

    with psycopg2.connect(database=data_base, user=user, password=password) as conn:

        create_tables(conn)
        id_client = add_client(conn,'Иван', 'Иванов','ivanov@mail.ru', '+79241111111',messages=False)
        id_client = add_client(conn, 'Петр', 'Петров','petrov@mail.ru', messages=False)
        add_phone(conn, id_client, '+79242222222', messages=False)
        id_client = add_client(conn, 'Сидор', 'Сидоров','sidorov@mail.ru', messages=False)
        add_phone(conn, id_client, '+79243333333', messages=False)

        key = input_key()
        while True:
            if key == '0':
                break
                # conn.close()
                # exit()
            if key == '1':

                name = input('Введите имя клиента: ')
                surname = input('Введите фамилию клиента: ')
                email = input('Введите e-mail клиента: ')
                add_client(conn)

            elif key == '2':

                id_client = input_id_clietn()
                if id_client_is_valid(id_client):
                    phone = input('Введите номер телефона: ')
                    add_phone(conn, id_client, phone)
                else:
                    print()
                    print(f'Клиент с id={id_client} не найден!')

            elif key == '3':

                id_client = input_id_clietn()
                if id_client_is_valid(id_client):
                    name = input('Введите имя клиента: ')
                    surname = input('Введите фамилию клиента: ')
                    email = input('Введите e-mail клиента: ')
                    update_clietn(conn, id_client, name, surname, email)
                else:
                    print()
                    print(f'Клиент с id={id_client} не найден!')

            elif key == '4':

                id_client = input_id_clietn()
                if id_client_is_valid(id_client):
                    phone = input('Введите номер телефона: ')
                    del_phone(conn, id_client, phone)
                else:
                    print()
                    print(f'Клиент с id={id_client} не найден!')

            elif key == '5':

                id_client = input_id_clietn()
                if id_client_is_valid(id_client):
                    del_client(conn, id_client)
                else:
                    print()
                    print(f'Клиент с id={id_client} не найден!')

            elif key == '6':

                name = input('Введите имя клиента: ')
                surname = input('Введите фамилию клиента: ')
                email = input('Введите e-mail клиента: ')
                phone = input('Введите телефон клиента: ')

                client_list = find_client(conn, name, surname, email, phone)
                print()
                print(*client_list, sep="\n")

            elif key == '7':

                client_list = all_client(conn)
                print()
                print(*client_list, sep="\n")

            elif key == '8':

                clear_all_phones(conn, True)

            elif key == '9':

                clear_all_client(conn, True)

            else:

                print('')
                print('Введено не верное значение!')

            print('')
            key = input_key()
