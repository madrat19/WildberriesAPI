
import psycopg2
from psycopg2 import Error
import json

# Делает запрос к базе данных
def Query(auth, query):
    try:
        connection = False
        connection = psycopg2.connect(user=auth['user'],
                                       password=auth['password'], host=auth['host'], port=auth['port'])
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()

    except (Exception, Error) as e:
        print("Error when working with PostgreSQL: ", type(e).__name__)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("The connection to PostgreSQL is closed")
        else:
            print('Failed to connect')

# Определяет типы данных SQL
def typeCheck(field, value):
    if 'date' in str(field) or 'Date' in str(field):
        return 'date'
    if type(value) == int:
        return 'integer'
    if type(value) == str:
        return 'varchar(255)'
    if type(value) == bool:
        return 'bool'
    return 'varchar(255)'
    
# Генерирует строку create запроса на основе json файла
def makeCreateQuery(file):
    data = []
    with open(file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    query = 'create table orders (\n'
    for field, value in data[0].items():
        string = str(field) + ' ' + typeCheck(field, value) + ',\n'
        query += string
    query = query[:-2]
    query += ');'

    return query



# Генерирует строку insert запроса на основе json файла
def makeInsertQuery(file, table):
    data = []
    with open(file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    query = 'insert into {} ('.format(table)
    for field in data[0].keys():
        string = str(field) + ', '
        query += string
    query = query[:-2]
    query += ')\n'
    query += 'values\n    ('
    for note in data:
        for value in note.values():
            string = "'" + str(value) + "'" + ', '
            query += string
        query = query[:-2]
        query += '),'
        query += '\n    ('
    query = query[:-7]
    query += ';'
    
    return query
    

    

# Делает два запроса к БД на создание таблицы и внесение в нее данных
# Код ожидает данные авторизации к БД в файле keys.py
# и данные от API в файле orders.json (создается скриптом getData.py) 
if __name__ == '__main__':
    import keys
    auth = keys.auth
    query = makeCreateQuery('orders.json')
    Query(auth, query)
    query = makeInsertQuery('orders.json', 'orders')
    Query(auth, query)  
    