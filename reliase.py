import json

from config import user_name
from db import create_connection
from functions import Function

connection = create_connection()



class Experiment:
    def __init__(self, first_element: str, second_element: str, temperature: int, source_data: dict, article: int):
        self.first_element = first_element
        self.second_element = second_element
        self.temperature = temperature
        self.source_data = source_data
        self.article = article

    # добавление эксперимента в бд
    def add_into_db(self):
        with (connection.cursor() as cursor):
            source_data_json = json.dumps(self.source_data)
            insert_query = "INSERT INTO experiments (first_element, second_element, temperature, source_data, article) VALUES " \
                           "('" + self.first_element + "', '" + self.second_element + "', '" + str(self.temperature) + "', '" + source_data_json + "', '" + str(self.article) + "');"
            cursor.execute(insert_query)
            connection.commit()


class Element:
    def __init__(self, name: str, specifications_string: str):
        self.name = name
        self.specifications_string = specifications_string

    # добавление элемента в бд
    def add_into_bd(self):
        with connection.cursor() as cursor:
            insert_query = "INSERT INTO elements (name, specifications) VALUES ('" + self.name + "', '" + self.specifications_string + "');"
            cursor.execute(insert_query)
            connection.commit()


class Attempt:
    count_attempts = 0
    def __init__(self,  id_exp: int, func: Function, id_method: int, init: dict, result: dict):
        self.id_exp = id_exp
        self.func = func
        self.id_method = id_method
        self.init = init
        self.result = result
        Attempt.count_attempts += 1
        self.number = Attempt.count_attempts

    def add_into_global_bd(self):
        try:
            init_data = json.dumps(self.init)
            result_data = json.dumps(self.result)
            with (connection.cursor() as cursor):
                insert_query = ("INSERT INTO attempts (experiment_id, func, method_id, init_data, result) "
                                "VALUES (" + str(self.id_exp) + ", '" + self.func.get_string() + "', " + str(self.id_method) +
                                ", '" + init_data + "', '" + result_data + "');")
                cursor.execute(insert_query)
                connection.commit()
        except Exception as ex:
            print(ex)



# для разбиения строки json формата в строку пользовательского формата
def crash(arr: list):
    s = str(arr).replace(', ', ',\n')
    s = s.replace('[','')
    s = s.replace(']','.')
    s = s.replace('\'', '')
    # while (s[0] == ' ' or s[0] == ',' or s[0] == '\n'):
    #     s = s[1:]
    return s

# получение словаря со всеми данными из бд об элементах
def get_all_elements(table_name: str):
    with connection.cursor() as cursor:
        select_all_rows = "SELECT * FROM " + table_name
        cursor.execute(select_all_rows)
        rows = cursor.fetchall()
        return rows


# для добавления в бд информации о попытке расчета
def add_attempt(id_exp: int, id_method: int, init: dict, result: dict):
    try:
        # init_a1, init_a2, result_a1, result_a2
        init_data = json.dumps(init)
        result_data = json.dumps(result)
        username = user_name
        with connection.cursor() as cursor:
            insert_query = ("INSERT INTO attempts (username, experiment_id, method_id, initial_a1, initial_a2, result_a1, result_a2) "\
                            "VALUES ('") + username + "', '" + str(id_exp) + "', '" + str(id_method) + "', '" + init_data + "', '" + result_data + "', '" + "');"
            cursor.execute(insert_query)
            connection.commit()
    except Exception as ex:
        print(ex)

# получение данных об эксперименте по его id
def get_experiment_as_id(id_exp: int):
    # with connection.cursor() as cursor:
    #     select_query = "SELECT * FROM experiments WHERE id = " + str(id_exp) + ";"
    #     cursor.execute(select_query)
    #     return cursor.fetchall()[0]
    with connection.cursor() as cursor:
        select_query = "SELECT * FROM experiments;"
        cursor.execute(select_query)
        return cursor.fetchall()[id_exp - 1]




# Для работы с базами данных вне классов
def delete_experiment(id_exp: int):
    with connection.cursor() as cursor:
        delete_query = "DELETE FROM experiments WHERE id = " + str(id_exp) + ";"
        cursor.execute(delete_query)
        connection.commit()

def add_article(name, author, year, link):
    with connection.cursor() as cursor:
        insert_query = "INSERT INTO articles (name, author, year, link) VALUES ('" + name + "', '" + author + "', '" + str(year) + "', '" + link + "');"
        cursor.execute(insert_query)
        connection.commit()

def delete_article(num):
    with connection.cursor() as cursor:
        delete_query = "DELETE FROM articles WHERE num = " + str(num) + ";"
        cursor.execute(delete_query)
        connection.commit()

def get_article_name(article_id:int):
    with connection.cursor() as cursor:
        select_query = f'SELECT name FROM articles WHERE id = {article_id};'
        cursor.execute(select_query)
        return cursor.fetchall()[0]['name']


# извлечение ветки элемента из базы данных
def get_branch(element_name: str)->list:
    with connection.cursor() as cursor:
        select_query = f'SELECT branch FROM elements WHERE name = \'{element_name}\''
        cursor.execute(select_query)
        branch = cursor.fetchall()
        return branch[0]['branch'].split(';')[:-1]


def get_ids_experiments_by_name(element_type: str)->list:
    stree = search.SearchTree()
    stree.make_all_branch()
    elements = stree.get_elements(element_type)
    print(elements)
    with connection.cursor() as cursor:
        select_query = 'SELECT id FROM experiments WHERE first_element = '
        for element in elements:
            select_query += '\'' + element + '\' OR '
        select_query += 'second_element = '
        for element in elements:
            select_query += '\'' + element + '\' OR '
        select_query = select_query[:len(select_query) - 4]
        select_query += ';'
        print(select_query)
        cursor.execute(select_query)
        res = cursor.fetchall()
        result = []
        for r in res:
            result.append(r['id'])
        return result

def bring_to_normal_filter(element_filter:list):
    for i in range(len(element_filter)):
        element = element_filter[i]
        element = element.lower()
        if element != 'not':
            first_letter = element[0].upper()
            element = first_letter + element[1:]
        element_filter[i] = element


def get_elements_list_by_filter(element_filter: str):
    from search import SEARCH_TREE
    filters_list = element_filter.split(' ')
    returned_list = []
    is_except = False
    for f in filters_list:
        if f == 'not':
            is_except = True
        else:
            if is_except:
                all_elements = SEARCH_TREE.get_elements('Any')
                except_elements = SEARCH_TREE.get_elements(f)
                returned_list += [i for i in all_elements if i not in except_elements]
            else:
                returned_list += SEARCH_TREE.get_elements(f)
            is_except = False
    return returned_list




# table USERS create
        # with connection.cursor() as cursor:
        #     create_table_query = "CREATE TABLE users (id int AUTO_INCREMENT, "\
        #                          "name varchar(32), "\
        #                          "password varchar(32), "\
        #                          "email varchar(32), PRIMARY KEY(id));"
        #     cursor.execute(create_table_query)
        #
        # table EXPERIMENTS create
        # with connection.cursor() as cursor:
        #     create_table_query = "CREATE TABLE experiments (id int AUTO_INCREMENT, "\
        #                          "first_element varchar(32), "\
        #                          "second_element varchar(32), "\
        #                          "temperature float(2), "\
        #                          "source_data JSON, "\
        #                          "article varchar(32), PRIMARY KEY(id));"
        #     cursor.execute(create_table_query)
        #
        # table ELEMENTS create
        # with connection.cursor() as cursor:
        #     create_table_query = "CREATE TABLE elements (id int AUTO_INCREMENT, " \
        #                          "name varchar(32), " \
        #                          "specifications varchar(512), PRIMARY KEY(id));"
        #     cursor.execute(create_table_query)
        #
        # table ATTEMPTS create
        # with connection.cursor() as cursor:
        #     create_table_query = "CREATE TABLE attempts (id int AUTO_INCREMENT, " \
        #                          "username varchar(32), " \
        #                          "experiment_id int, " \
        #                          "method_id int, " \
        #                          "initial_a1 float, " \
        #                          "initial_a2 float, " \
        #                          "result_a1 float, " \
        #                          "result_a2 float, PRIMARY KEY(id));"
        #     cursor.execute(create_table_query)
        #
        # table ARTICLES create
        # with reliase.connection.cursor() as cursor:
        #     create_table_query = "CREATE TABLE articles (id int AUTO_INCREMENT, "\
        #                          "name varchar(64), "\
        #                          "author varchar(64), "\
        #                          "year int, "\
        #                          "link varchar(128), PRIMARY KEY(id));"
        #     cursor.execute(create_table_query)

if __name__ == '__main__':
    element_filter = ['etHanOl', 'not', '1-hexanol']
    bring_to_normal_filter(element_filter)
    print(element_filter)