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
    phantom = Phantom()
    conf = {
        'url': url + '#zakupki_mini',
        'min_wait': 2000,
        'max_wait': 30000,
        'resource_timeout': 3000,
        'headers': {
            'User-Agent': USER_AGENT,
            'Referer': 'https://zachestnyibiznes.ru/' + str(inn)
        },
    }
    page = phantom.download_page(conf)
    current_data = []
    soup = BeautifulSoup(page, "html.parser")
    name = soup.find('h1', "f-s-25 m-t-0 m-b-5")
    current_data.append(['name', name.find('b').text])
    main_info = soup.find_all('div', class_='col-md-6')[2]
    tags = main_info.find_all('p', class_='no-indent m-b-0')
    values = main_info.find_all('p', class_='m-b-10 no-indent')
    for k in range(len(tags)):
        tmp = tags[k].find('b')
        if tmp:
            tmp = tmp.text
            if tmp == 'ИНН':
                txt = values[k].text
                txt = txt.replace('\n', '')
                current_data.append(['inn', txt])
            elif tmp == 'ОГРН':
                txt = values[k].text
                txt = txt.replace('\n', '')
                txt = txt[0:txt.find('от')]
                current_data.append(['ogrn', txt])
            elif tmp == 'Статус':
                txt = values[k].text
                txt = txt.replace('\n', '')
                current_data.append(['status', txt])
    blocks = soup.find_all('div', class_='background-white margin-mobile b-radius-3 p-20 m-b-20')
    for block in blocks:
        h = block.find('p', class_='list-group-item-heading f-s-18 no-indent')
        if h:
            h = h.find('b').text
            if h.find('Aффилированность') > -1:
                affiliation = block.find_all('b', class_='f-s-12')
                affiliation_values = block.find_all('b', class_='f-s-18')
                for k in range(len(affiliation)):
                    current_data.append([affiliation[k].text, affiliation_values[k].text.replace('\n', '')])
    current_data.append(['courts', soup.find('a', id='arb_total').text])
    government_contracts = soup.find('div', id='customer-top')
    if government_contracts:
        details = government_contracts.find_all('a', class_='no-underline')
        current_data.append(['government_contracts_amount', details[0].text])
        current_data.append(['government_contracts_total', details[1].text.replace(' руб.', '')])
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
    try:
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
    except:
        pass
    try:
        finance_reporting = soup.find(id='fin-stat-fns')
        all_reports = finance_reporting.find_all('tr')
        for report in all_reports:
            if report.style != "background: #dddddd;":
                info = report.find_all('td')
                if info:
                    prefix = info[0].text
                    prefix = prefix[0:prefix.find('Дата')]
                    prefix = prefix.replace('\n', '')
                    for k in range(1, len(info)):
                        value = info[k].text.replace('\n', '')
                        current_data.append([prefix + info[k]['data-th'].replace(':', ''), value])
    except:
        pass
    return current_data


def data_from_purchases_page(url):
    time.sleep(1)
    phantom = Phantom()
    conf = {
        'url': url + '/zakupki',
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
    soup = BeautifulSoup(page, 'html.parser')
    try:
        provider = soup.find('p', class_='lead').text.split(' ')
    except:
        provider = [0]
    current_data.append(['provider', provider[len(provider) - 1]])
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
            current_data += data_from_purchases_page(url)
            result.append(current_data)
    return result
