import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3


FIXTURES = ['date', 'comp', 'round', 'dayofweek', 'venue', 'result', 'goals_for', 'goals_against', 'opponent',
            'possession', 'attendance', 'captain', 'formation', 'referee']
LEAGUES = ['9/stats/Premier-League-Stats']
MAIN_LINK = 'https://fbref.com'


def get_teams(url: str) -> list:
    """
    Функция для поиска ссылок на все команды чемпионата
    :param url: ссылка конкретного турнира
    :return:список со всеми командными ссылками
    """
    res = requests.get(url).content
    soup = BeautifulSoup(res, 'html.parser')
    all_tables = soup.findAll('table')[0]
    links = [MAIN_LINK + a.get('href') for a in all_tables.find_all('a')]
    return links


def get_response_team(url: list) -> list:
    """
    Функция собирает все данные по каждой команде
    :param url: ссылка на данные матчей конкретной команды
    :return: список с информацией всех матчей в разрезе каждой команды
    """
    list_data_team = []
    for link in url:
        res = requests.get(link).content
        soup = BeautifulSoup(res, 'html.parser')
        data_team = soup.findAll('table')[1]
        list_data_team.append(data_team)
    return list_data_team


def get_frame_team(features: list, data_teams: list) -> dict:
    """
    Функция собирает статистику по командам и сохраняет в Dataframe
    :param features: показатели, которые собираются по каждой команде
    :param data_teams: спарсенные данные по конкретной команде
    :return: dataframe
    """

    for team in data_teams:
        name_team = \
            team.find('caption').text.split(': All Competitions Table')[0].split('Scores & Fixtures 2021-2022 ')[1]
        pre_df_squad = {}
        features_wanted_squad = features
        rows_squad = team.find_all('tr')
        for row in rows_squad:
            if row.find('th', {"scope": "row"}) is not None:
                if name_team in pre_df_squad:
                    pre_df_squad['squad'].append(name_team)
                else:
                    pre_df_squad['squad'] = [name_team]
                for f in features_wanted_squad:
                    cell = row.find("td", {"data-stat": f}) or row.find("th", {"data-stat": f})
                    a = cell.text.strip().encode()
                    text = a.decode("utf-8")
                    if text == '':
                        text = '0'
                    if (f != 'result') & (f != 'venue') & (f != 'dayofweek') & (f != 'round') & (f != 'comp') \
                            & (f != 'opponent') & (f != 'captain') & (f != 'formation') \
                            & (f != 'referee') & (f != 'date'):
                        try:
                            text = int(text.replace(',', ''))
                        except ValueError:
                            text = text.strip(' ')[0]
                    if f in pre_df_squad:
                        pre_df_squad[f].append(text)
                    else:
                        pre_df_squad[f] = [text]

        pre_df_squad['squad'] *= len(pre_df_squad['venue'])
        df_squad = pd.DataFrame.from_dict(pre_df_squad)

        df_squad = df_squad[df_squad['comp'] == 'Premier League']
        return df_squad


def save_sql(df_squad) -> None:
    """
    Функция для сохранения данных в БД
    :param df_squad: Dataframe с итоговыми данными по командам
    """
    conn = sqlite3.connect(r'C:\Users\user\PycharmProjects\Eqvanta\flask_auth_app\project\db.sqlite', timeout=10)
    df_squad.to_sql('fbref', conn, schema=None, if_exists='append', index=True, index_label=None,
                    chunksize=None, dtype=None, method=None)
    conn.close()
    print('Данные записаны в таблицу БД')


if __name__ == '__main__':
    for league in LEAGUES:
        league_name = league.rsplit('/', maxsplit=1)[-1]
        url = ('https://fbref.com/en/comps/' + f'{league}')  # формируем ссылку на лигу
        team_table = get_teams(url)  # получаем ссылки на все команды
        data_teams = get_response_team(team_table)  # получаем данные по матчам каждой команды
        df_squad = get_frame_team(FIXTURES, data_teams)
        save_sql(df_squad)
