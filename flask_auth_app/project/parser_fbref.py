import sqlite3
import requests
from collections import defaultdict

from bs4 import BeautifulSoup

from work_for_sql import Database

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
    return {name.text: MAIN_LINK + name.get('href') for name in data_html.find_all('a')}


def get_response_team(links: dict) -> list:
    """
    The function collects all data by command
    :param links: dictionary with meaning in the form of links to the team's match data
    :return:html format with information of all matches in the context of each team
    """
    list_data_team = []
    count = 0
    for name, link in links.items():
        res = requests.get(link).content
        soup = BeautifulSoup(res, 'html.parser')
        data_team = soup.find('table', {'id': 'matchlogs_for'})
        list_data_team.append((name, data_team))
        count += 1
        if count == 10:
            break
    return list_data_team


def get_frame_team(features: list, data_teams: list) -> dict:
    """
    The function collects statistics on commands and saves them to the dictionary
    :param features: indicators that are collected for each team
    :param data_teams: collected data for a specific team
    :return: dictionary of all league matches of the whole season
    """
    squad = defaultdict(list)
    for name_team, table in data_teams:
        for row in table.findAll('tr')[1:]:
            pre_dict = {}
            for feature in features:
                cell = row.find(attrs={"data-stat": feature}).text.strip()
                try:
                    cell = int(cell.replace(',', '.'))
                except ValueError:
                    pass
                pre_dict[feature] = cell
            squad[name_team].append(pre_dict)
    return squad




# написать класс
def save_sql(df_squad) -> None:
    """
    Функция для сохранения данных в БД
    :param df_squad: Dataframe с итоговыми данными по командам
    """
    conn = sqlite3.connect(r'/db.sqlite', timeout=10)
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
        df_squad = get_frame_team(FIXTURES, data_teams)
        # save_sql(df_squad)
        sql = Database(r'/db.sqlite')
        sql

