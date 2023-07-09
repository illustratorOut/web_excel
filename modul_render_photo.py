import sqlite3


def get_developer_info(art):
    try:
        sqlite_connection = sqlite3.connect('sqlite_python.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sql_select_query = """select * from photo_rus where art = ?"""
        cursor.execute(sql_select_query, (art,))
        records = cursor.fetchall()

        for row in records:
            print("ID:", row[0])
            print("Имя:", row[1])
            # print("Почта:", row[2])
            print("Добавлен:", row[3], end="\n\n")
            return row[2]
        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")
