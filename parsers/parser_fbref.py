import sys

import requests

sys.path.append('C:\\Users\\user\\PycharmProjects\\Eqvanta')

from bs4 import BeautifulSoup
from for_sql.work_for_sql import Database

from config import path_to_dbase



FIXTURES = ['date', 'comp', 'round', 'dayofweek', 'venue', 'result', 'goals_for', 'goals_against', 'opponent',
            'possession', 'attendance', 'captain', 'formation', 'referee']
LEAGUES = ['9/stats/Premier-League-Stats']
MAIN_LINK = 'https://fbref.com'


def get_teams(url: str) -> dict[str, str]:
    """
    Функция поиска ссылок на все команды чемпионата.
    :param url: ссылка на турнир.
    :return: словарь: название команды и ссылка на ее данные.
    """
    res = requests.get(url).content
    soup = BeautifulSoup(res, 'html.parser')
    data_html = soup.find('table', {'id': 'stats_squads_standard_for'})
    return {name.text: MAIN_LINK + name.get('href') for name in data_html.find_all('a')}


def get_response_team(links: dict) -> list:
    """
    Функция собирает все данные команды.
    :param links:словарь с названием команды и ссылками на ее матчи.
    :return: html формат данных всех матчей команды.
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


def get_frame_team(features: list, datas_teams: list) -> list:
    """
    Функция собирает статистику по командам
    :param features: показатели, которые собираются для каждой команды.
    :param datas_teams: собранные данные для конкретной команды.
    :return: список словарей всех матчей лиги за весь сезон
    """
    squad = list()
    for name_team, table in datas_teams:
        for row in table.findAll('tr')[1:]:
            pre_dict = {}
            for feature in features:
                cell = row.find(attrs={"data-stat": feature}).text.strip()
                try:
                    cell = int(cell.replace(',', '.'))
                except ValueError:
                    pass
                pre_dict[feature] = cell
            pre_dict["squad"] = name_team
            squad.append(pre_dict)
    return squad


if __name__ == '__main__':
    for league in LEAGUES:
        url = 'https://fbref.com/en/comps/' + league  # формирование общей ссылки на турнир
        team_table = get_teams(url)  # получение всех ссылок на команды
        name_teams = team_table.keys()
        data_teams = get_response_team(team_table)  # получение всех матчей каждой команды
        df_squad = get_frame_team(FIXTURES, data_teams)

        with Database(path_to_dbase) as dbase:
            sel = dbase.select('count(*)', limit=10_000)
