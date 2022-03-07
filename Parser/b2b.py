from bs4 import BeautifulSoup
import requests
import time


# Константа для корректной работы
USER_AGENT = 'Mozilla/5.0'


# Получение айдишника категории по названию
# Аргумент - название категории
# Возвращаемое значение - айдишник категории
# ToDo написать нормальное отображение, пока оно просто считает, что все болты свободные
def get_category_id(name):
    if name == 'metalware':
        return 42714840


def get_links_to_sellers_by_category_id(cat_id, offset):
    is_there_more = True
    current_from = offset
    links = []
    while is_there_more:
        time.sleep(2)
        is_there_more = False
        url = f"https://www.b2b-center.ru/firms/?show=sellers&cat_id={cat_id}&from={current_from}"
        page = requests.get(url, headers={
            'User-Agent': USER_AGENT,
            'Referer': "https://www.b2b-center.ru/firms/?show=sellers"
        })
        soup = BeautifulSoup(page.text, "html.parser")
        sellers = soup.find_all('a', class_='visited')
        if sellers:
            for seller in sellers:
                links.append(seller["href"])
            is_there_more = True
        current_from += 20
    return links


def get_inns_by_category(name, offset):
    inns = []
    cat_id = get_category_id(name)
    all_links = get_links_to_sellers_by_category_id(cat_id, offset)
    for url in all_links:
        time.sleep(2)
        page = requests.get("https://www.b2b-center.ru" + url, headers={
            'User-Agent': USER_AGENT,
            'Referer': f"https://www.b2b-center.ru/firms/?show=sellers&cat_id={cat_id}"
        })
        soup = BeautifulSoup(page.text, "html.parser")
        sellers = soup.find_all('td')
        for i in range(len(sellers) - 1):
            if sellers[i].text == 'ИНН':
                inns.append(int(sellers[i + 1].text))
                print(int(sellers[i + 1].text))
    return inns
