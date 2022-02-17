import sqlite3

# убрать хардкод. сделать контекстный менеджер, добавить исключения


class Database:

    def __init__(self, **kwargs):
        self.filename = kwargs.get('filename')
        self.table = kwargs.get('table')

    def insert(self, row, table):
        self._db.execute('insert into {} (squad, date, comp, round, dayofweek, venue, result, goals_for,goals_against,'
                         'opponent, possesion, attendance, captain, formation, referee)'
                         'values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'.format(table),
                         (row['squad'], row['date'], row['comp'], row['round'], row['dayofweek'], row['venue'],
                          row['result'], row['goals_for'], row['goals_against'], row['opponent'], row['possesion'],
                          row['attendance'], row['captain'], row['formation'], row['referee']))
        self._db.commit()


def main():
    db = sqlite3.connect(r'/db.sqlite', timeout=10)
    # db = Database(filename='db.sqlite', table='fbref')
    # conn = sqlite3.connect(r'C:\Users\user\PycharmProjects\Eqvanta\flask_auth_app\project\db.sqlite', timeout=10)

    print('Create rows')
    db.insert(dict(squad='Arsenal_t', date='2021-08-22', comp='Premier League', round='Matchweek 45', dayofweek='Fri',
                   venue='Away', result='W', goals_for=3, goals_against=0, opponent='Brentford', possesion=35,
                   attendance=3000, captain='Tyrone', formation='4-3-3', referee='Anthony Taylor'), 'fbref')

if __name__ == "__main__":
    main()
