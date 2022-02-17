import sqlite3
import requests
from itertools import product
from collections import defaultdict

from bs4 import BeautifulSoup
import pandas as pd


FIXTURES = ['date', 'comp', 'round', 'dayofweek', 'venue', 'result', 'goals_for', 'goals_against', 'opponent',
            'possession', 'attendance', 'captain', 'formation', 'referee']
LEAGUES = ['9/stats/Premier-League-Stats']
MAIN_LINK = 'https://fbref.com'

# пути не хардкодить. Нужно использовать venv. И как использовать относительный путь, чтобы ссылаться из текущей директории.


def get_teams(url: str) -> dict[str, str]:
    """
    Function to search for links to all championship teams
    :param url: link to a tournament
    :return: dictionary in the size of the name and link of the commands
    """
    res = requests.get(url).content
    soup = BeautifulSoup(res, 'html.parser')
    data_html = soup.find('table', {'id': 'stats_squads_standard_for'})
    links_teams = [MAIN_LINK + a.get('href') for a in data_html.find_all('a')]
    names_teams = [name.text for name in data_html.find_all('a')]
    return dict(zip(names_teams, links_teams))


def get_response_team(links: dict) -> list:
    """
    The function collects all data by command
    :param links: dictionary with meaning in the form of links to the team's match data
    :return:html format with information of all matches in the context of each team
    """
    list_data_team = []
    for link in links.values():
        res = requests.get(link).content
        soup = BeautifulSoup(res, 'html.parser')
        data_team = soup.find('table', {'id': 'matchlogs_for'})
        list_data_team.append(data_team)
    return list_data_team


def get_frame_team(features: list, data_teams: list, team_table):  # исправить return
    """
    Функция собирает статистику по командам и сохраняет в Dataframe
    :param features:показатели, которые собираются по каждой команде
    :param data_teams:спарсенные данные по конкретной команде
    :param name_teams:данные с названиями команд
    :return: dataframe всех матчей лиги всего сезона
    """
    # pre_df_squad = defaultdict(dict)  # Значения по дефолту. Есть библиотека. Наверно defaultdict
    pre_df_squad = {}  # Значения по дефолту. Есть библиотека. Наверно defaultdict
    lis = []
    dict_of_teams = dict()
    for team_html in data_teams:
    #     # print(team_html.find_all('tr'))
    #     # rows_squad = team_html.find_all('tr')
        for row, feature, name in product(team_html.find_all('tr'), features, team_table):
            dict_of_teams[name] = []
            if row.find('th', {"scope": "row"}):  # можно первым значением указать **kwargs
                cell = row.find("td", {"data-stat": feature}) or row.find("th", {"data-stat": feature})
                print(cell.text)
                # dict_of_teams[name] = lis.append({feature: cell.text})
                dict_of_teams[name].append(cell.text)
                # lis.append({feature: cell.text})
            # pre_df_squad.update({name: lis})
    # print(dict_of_teams)
    # print(pre_df_squad)
        #
        # return df_squad

# написать класс
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
        url = 'https://fbref.com/en/comps/' + league  # формируем ссылку на лигу
        team_table = get_teams(url)  # получаем ссылки на все команды
        name_teams = team_table.keys()
        data_teams = get_response_team(team_table)  # получаем данные по матчам каждой команды
        df_squad = get_frame_team(FIXTURES, data_teams, team_table)
        # save_sql(df_squad)
