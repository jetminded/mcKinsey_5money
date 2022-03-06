from bs4 import BeautifulSoup
from phantomjs import Phantom
import requests
import time


# Константа для корректной работы
USER_AGENT = 'Mozilla/5.0'


# Находит ссылки на страницы всех организаций с данным ИНН
# Аргумент - ИНН
# Возвращает массив ссылок
def get_links_by_inn(inn):
    time.sleep(1)
    url = f"https://zachestnyibiznes.ru/search?query={inn}"
    page = requests.get(url, headers={
        'User-Agent': USER_AGENT,
        'Referer': 'https://zachestnyibiznes.ru/'})
    print("Page status: ", page.status_code)
    soup = BeautifulSoup(page.text, "html.parser")
    all_organizations = soup.find_all('div', class_="m-t-25")
    links = []
    for organization in all_organizations:
        links.append("https://zachestnyibiznes.ru" + organization.find('a', class_="no-underline f-s-16",
                                                                       itemprop="legalName")['href'])
    return links


# Получает информацию с главной стрицы (название, инн, рейтинг, статус)
# Аргументы - ссылка на главную стриницу, ИНН
# Возвращает массив пар вида "имя параметра" - "значение"
def data_from_main_page(url, inn):
    time.sleep(1)
    page = requests.get(url, headers={
        'User-Agent': USER_AGENT,
        'Referer': 'https://zachestnyibiznes.ru/' + str(inn)})
    print("Page status: ", page.status_code)
    current_data = []
    soup = BeautifulSoup(page.text, "html.parser")
    name = soup.find('h1', "f-s-25 m-t-0 m-b-5")
    current_data.append(['name', name.find('b').text])
    current_data.append(['inn', inn])
    status = soup.find('p', class_='m-b-10 no-indent')
    current_data.append(['status', status.find('b').text])
    try:
        rating = soup.find('span', class_='box-rating')
        current_data.append(['rating', rating.find('b').text])
    except:
        return []
    return current_data


# Получает информацию о финансовом отчете компании
# Аргумент - ссылка на основную страницу компании
# Возвращает массив пар вида "имя параметра" - "значение"
def data_from_finance_page(url):
    time.sleep(1)
    phantom = Phantom()
    conf = {
        'url': url + '/balance',
        'min_wait': 1000,
        'max_wait': 30000,
        'resource_timeout': 3000,
        'headers': {
            'User-Agent': USER_AGENT,
            'Referer': url
        },
    }
    page = phantom.download_page(conf)
    current_data = []
    soup = BeautifulSoup(page, "html.parser")
    balance_list = soup.find(id="balance_list")
    all_data = balance_list.find_all('p', class_="no-indent")
    for data in all_data:
        key = data.find(text=True)
        key = key.replace("\n", '')
        key = key.replace(u'\xa0', '')
        if key != "Внимание:" and key != "Финансовый анализ":
            try:
                current_data.append([key, float(data.find('span').text)])
            except:
                current_data.append([key, float(0)])
                print(url)
    return current_data


# Находит всю информацию о компаниях с данным ИНН
# Единственный параметр - инн в формате числа
# Возвращает список с информацией о каждой компании с данным ИНН
def get_data_by_inn(inn):
    links = get_links_by_inn(inn)
    result = []
    for url in links:
        current_data = data_from_main_page(url, inn)
        if current_data:
            current_data += data_from_finance_page(url)
            result.append(current_data)
    return result
