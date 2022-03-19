"""
Парсинг сайта b2b-center.tu
"""

import time
from bs4 import BeautifulSoup
from phantomjs import Phantom


# Константа для корректной работы
USER_AGENT = 'Yandex/5.0'


def get_category_id(name):
    """
    Получение айдишника категории по названию
    Аргумент - название категории
    Возвращаемое значение - айдишник категории
    """
    if name == 'metalware':
        return 42714840
    if name == 'rubber':
        return 42519524


def get_links_to_sellers_by_category_id(cat_id, offset) -> []:
    """
    Получение ссылок на страницы поставщиков данной категории
    """
    is_there_more = True
    current_from = offset
    links = []
    counter = 0
    while is_there_more:
        if counter % 10 == 0:
            time.sleep(30)
        time.sleep(3)
        is_there_more = False
        phantom = Phantom()
        url = f"https://www.b2b-center.ru/firms/?show=sellers&cat_id={cat_id}&from={current_from}"
        conf = {
            'url': url,
            'min_wait': 1000,
            'max_wait': 30000,
            'resource_timeout': 3000,
            'headers': {
                'User-Agent': USER_AGENT,
                'Referer': "https://www.b2b-center.ru/firms/"
            },
        }
        page = phantom.download_page(conf)
        soup = BeautifulSoup(page, "html.parser")
        sellers = soup.find_all('a', class_='visited')
        if sellers:
            for seller in sellers:
                links.append(seller["href"])
            is_there_more = True
        current_from += 20
        counter += 1
    return links


def get_inns_by_category(name, offset) -> []:
    """
    Парсинг ИНН по данной категории
    """
    inns = []
    cat_id = get_category_id(name)
    all_links = get_links_to_sellers_by_category_id(cat_id, offset)
    counter = 0
    for url in all_links:
        if counter % 10 == 0:
            time.sleep(30)
        time.sleep(3)
        phantom = Phantom()
        conf = {
            'url': "https://www.b2b-center.ru" + url,
            'min_wait': 1000,
            'max_wait': 30000,
            'resource_timeout': 3000,
            'headers': {
                'User-Agent': USER_AGENT,
                'Referer': f"https://www.b2b-center.ru/firms/?show=sellers&cat_id={cat_id}"
            },
        }
        page = phantom.download_page(conf)
        soup = BeautifulSoup(page, "html.parser")
        sellers = soup.find_all('td')
        for i in range(len(sellers) - 1):
            if sellers[i].text == 'ИНН':
                inns.append(int(sellers[i + 1].text))
        counter += 1
    return inns
