# import sqlite3
# import reliase

# connection = sqlite3.connect('main_database.db')

# cursor = connection.cursor()

# # select_query = 'SELECT * FROM elements'
# # cursor.execute(select_query)
# # print(cursor.fetchall())
# # insert_query = 'INSERT INTO elements (name, branch) VALUES("1-Chlorobutane", "alcohol")' #[{'id': 1, 'name': '1-Chlorobutane', 'branch': 'alcohol;'}
# # cursor.execute(insert_query)
# # create_query = "CREATE TABLE articles (id INTEGER PRIMARY KEY AUTOINCREMENT, "\
# #                                  "name TEXT, "\
# #                                  "author TEXT, "\
# #                                  "year INTEGER, "\
# #                                  "link TEXT);"
# # cursor.execute(create_query)
# # drop_query = 'DROP TABLE articles'
# # cursor.execute(drop_query)

# # articles = reliase.get_all_elements('articles')
# # for article in articles:
# #     insert_query = f"INSERT INTO articles (name, author, year, link) VALUES ('{article['name']}', '{article['author']}', {article['year']}, '{article['link']}');"
# #     cursor.execute(insert_query)

# connection.commit()
# connection.close()