from flask import Flask, request
import requests
from bs4 import BeautifulSoup as bs

app = Flask(__name__)

@app.route('/live/', methods=['GET'])
def html():
    url = 'https://football.kulichki.net/live.htm'
    html_response = requests.get(url).content
    soup = bs(html_response, 'html.parser').find('table')
    return str(soup)


if __name__ == '__main__':
    app.run(debug=True)


