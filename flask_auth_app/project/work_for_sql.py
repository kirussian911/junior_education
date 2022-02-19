import sqlite3 as sql

from config import path_to_dbase, table


class Database:

    def __init__(self, dbname):
        """
        :param dbname: полный путь к базе данных
        """
        try:
            self.dbname = dbname
            self.conn = sql.connect(dbname)
            self.cursor = self.conn.cursor()
        except (sql.Error, sql.Warning) as error:
            print("He удалось подключиться к БД", error)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.conn.commit()
        self.conn.close()
        if exc_value:
            raise

    def select(self, table: str, limit=None) -> list:
        """
        SELECT метод
        :param table: название таблицы
        :param limit: количество записей из таблицы для вывода
        :return: список данных
        """
        try:
            query_row = f'SELECT * FROM {table}'
            if limit:
                query_row = f'SELECT * FROM {table} LIMIT {limit}'
            select_rows = self.cursor.execute(query_row)
            columns = [row[0] for row in select_rows.description]
        except (sql.Error, sql.Warning) as error:
            print("Ошибка:", error)

        return list(map(lambda row: dict(zip(columns, row)), self.cursor.fetchall()))

    def insert(self, table: str, **kwargs):
        """
        INSERT метод
        :param table: название таблицы
        :param kwargs: переданные параметры
        :return: результат запроса
        """
        columns = tuple([x for x in kwargs.keys()])
        values = tuple([y for y in kwargs.values()])
        try:
            query = f"INSERT INTO {table} {columns} VALUES {values}"
            self.cursor.execute(query)
            self.conn.commit()
            print('Данные успешно записаны в БД')
        except sql.IntegrityError as error:
            print("Error occurred: ", error)

        return self.cursor.execute(f"SELECT * FROM {table}")


def main():
    dbase = Database(path_to_dbase)
    # dbase.select('fbref', limit=1)
    # data = {'squad': '222', 'date': '2021-08-14', 'comp': 'Premier League', 'round': 'Matchweek 1',
    #         'dayofweek': 'Sat', 'venue': 'Away', 'result': 'L', 'goals_for': 0, 'goals_against': 1,
    #         'opponent': 'Leicester City', 'possession': 100, 'attendance': 31983, 'captain': 'Conor Coady',
    #         'formation': '3-4-3', 'referee': 'Craig Pawson'}
    # dbase.insert(table=name_table, **data)


if __name__ == "__main__":
    main()
