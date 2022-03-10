import logging
import sqlite3 as sql
from typing import Any

from config import table_name



class Database:
    __doc__ = """Класс для обработки SELECT и INSERT методов при работе с БД"""

    def __init__(self, path_to_dbase: str):
        """
        :param path_to_dbase: полный путь к базе данных
        """
        try:
            self.db_path = path_to_dbase
            self.table_name = table_name
            self.conn = sql.connect(path_to_dbase)
            self.cursor = self.conn.cursor()
        except (sql.Error, sql.Warning) as error:
            logging.exception("He удалось подключиться к БД", error)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.conn.commit()
        self.conn.close()
        if exc_value:
            raise

    def select(self, *args, limit=Any | None, **data: dict[str, Any], ) -> list:
        """
        SELECT метод
        :param limit: количество записей из таблицы для вывода
        :param data: условия для выборки
        :return: список данных
        """
        try:
            term_where = "SELECT {} FROM {} ".format(','.join(args), self.table_name)
            if len(data) > 1:
                term_where += "WHERE "
                term_where += " AND ".join(f"{k} = '{v}'" for k, v in data.items())
            select_rows = self.cursor.execute(term_where + " LIMIT %d" % (limit))
            columns = [row[0] for row in select_rows.description]
        except (sql.Error, sql.Warning) as error:
            logging.exception('Ошибка: ', error)
        return list(map(lambda row: dict(zip(columns, row)), self.cursor.fetchall()))

    def insert(self, **kwargs: dict[str, Any]):
        """
        INSERT метод
        :param kwargs: переданные параметры
        """
        columns = ",".join(f'"{k}"' for k in kwargs.keys())
        values = ",".join(f'"{v}"' for v in kwargs.values())
        try:
            self.cursor.execute("INSERT INTO {} ({}) VALUES ({})".format(self.table_name, columns, values))
        except sql.OperationalError as error:
            logging.exception(values, 'Ошибка: ', error)
        self.conn.commit()
        logging.info('Данные успешно записаны в БД')
