import requests
from bs4 import BeautifulSoup as bs4

URL = 'https://gbstore.ru/categories/macbook-pro-16-2019'


def get_html(url):
    response = requests.get(url)
    return response.text


def norm_article(article: str):
    article = str(article.replace(' ', '').replace('\n', ''))
    return article.strip()


def norm_name(name: str):
    name = name.split('(')[-1][0:-1]
    return name


def norm_price(price: str):
    price = int(price.replace(' ', ''))
    return price


def get_data(html):
    item_list = []
    soup = bs4(html, 'lxml')
    positions = soup.find_all('div', class_='products-view-block js-products-view-block products-view-block-static')
    for position in positions:
        pos_article = position.find('div', class_='col-xs-8 align-right').text
        pos_name = position.find('span', class_='products-view-name-link').text
        pos_price = position.find('div', class_='price-number').text
        data = {'article': norm_article(pos_article),
                'name': norm_name(pos_name),
                'price': norm_price(pos_price)}
        # print(f'Артикул: {norm_article(pos_article)}')
        # print(f'Наименование: {norm_name(pos_name)}')
        # print(f'Цена: {norm_price(pos_price)} руб.')
        # print('=' * 20)
        # print(data)
        item_list.append(data)
    return item_list


def main_data():
    return get_data(get_html(URL))



