import re
from functools import lru_cache

import requests
from bs4 import BeautifulSoup as bs


@lru_cache(maxsize=50)
def get_url_match(date_match: str, home_team: str, away_team: str) -> str:
    """
    Функция поиска статистики конкретного матча
    :param date_match: дата матча
    :home_team: название домашней команды
    :away_team: название гостевой команды
    :return: ссылка на выбранный матч
    """
    url_match = ''
    res = requests.get('https://fbref.com/en/matches/' + date_match).text
    soup = bs(res, 'html.parser')
    country = soup.find('div', {'id': 'content'}).find_all('tr')

    for html in country:
        home = html.find('td', {'data-stat': 'squad_a'})
        away = html.find('td', {'data-stat': 'squad_b'})
        if home is not None and away is not None:
            if home_team == home.text and away_team == away.text:
                url_match = 'https://fbref.com/' + \
                    html.find('td', {'data-stat': 'score'}).find('a').get('href')
    return url_match



@lru_cache(maxsize=50)
def get_response_match(link: str) -> dict:
    """
    Функция собирает данные матча
    :param link: ссылка на матч
    :return: словарь со статистикой матча
    """
    data_team = {}

    res = requests.get(link).content
    soup = bs(res, 'html.parser')

    round_match = soup.find('div', {'class': 'scorebox_meta'}).find_all('div')[1].text
    matchweek = 'Matchweek ' + str(re.search(r'\d+', round_match).group())
    home_goal, away_goal = [x.text for x in soup.select(".score")]
    result = 'W' if home_goal > away_goal else 'D' if home_goal == away_goal else 'L'
    posession = soup.find('div', {'id': 'team_stats'}).select('td')[0].text.strip()
    attendance = soup.find('div', {'class': 'scorebox_meta'}).find_all('div')[4].text.replace(',', '.')
    attendance = str(re.search(r'\d+.\d+', attendance).group())
    captain = soup.select('.datapoint')[1].text.split(':')[1].strip()

    formation = soup.find('div', {'class': 'lineup'}).find('th').text
    formation = "".join(re.findall(r'\d-+|\d+', formation))

    referee = soup.find('div', {'class': 'scorebox_meta'}).find_all('div')[6].text
    referee = re.search(r'Officials: (.*?) \(Referee\)', referee).group(1)

    data_team.update({
               'matchweek': matchweek, 'home_goal': home_goal,
               'away_goal': away_goal, 'result': result,
               'posession': posession, 'attendance': attendance,
               'captain': captain, 'formation': formation, 'referee': referee
               })
    return data_team
