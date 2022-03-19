"""
Рассчет рейтинга организаций и все необходимое для него
"""

import datetime
from org_by_inn import get_all_info_by_inn


def age(date):
    """
    Получение веремени работы организации
    """
    date = date.split('.')
    date_d = datetime.date(int(date[2]), int(date[1]), int(date[0]))
    now = datetime.date.today()
    return float(str(now - date_d).split()[0]) / 365


def scale(value, min_v, max_v):
    """
    Вспомогательная информация для линейной нормировки показателя
    """
    if value < min_v:
        return 0
    if value > max_v:
        return 1
    return (value - min_v) / (max_v - min_v)


def get_equity_capital(org) -> float:
    """
    Вспомогательная функция по расчету собственного капитала
    """
    equity_capital = org['Уставный капитал (складочный капитал, уставный фонд, вклады товарищей) 2020 ']
    equity_capital += org['Уставный капитал (складочный капитал, уставный фонд, вклады товарищей) 2019 ']
    equity_capital += org['Добавочный капитал (без переоценки) 2020 '] + \
          org['Добавочный капитал (без переоценки) 2019 ']
    equity_capital += org['Резервный капитал 2020 '] + org['Резервный капитал 2019 ']
    equity_capital /= 2
    return equity_capital


def org_size(org) -> None:
    """
    Расчет размера организации
    """
    org['size'] = 0.25 * max(0, min(org['Филиалы'], 1))
    org['size'] += 0.25 * max(0, min(org['Учреждённые'], 1))
    org['size'] += 0.25 * max(0, min(org['Представительства'], 1))
    org['size'] += 0.25 * max(0, min(org['Управляемые'], 1))
    org['size'] *= 10


def get_experience_info(org) -> {}:
    """
    Информация об опыте компании как поставщика
    """
    try:
        org_size(org)
    except (ValueError, KeyError, TypeError):
        org['size'] = 'Нет данных'
    try:
        org['stability'] = age(org['date'])
        org['stability'] = 0.6 * scale(age(org['date']), 0.0833, 3)
        if 'Положительный факт: Юридический адрес' in org:
            org['stability'] += 0.4
        org['stability'] *= 10
    except (ValueError, KeyError, TypeError):
        org['stability'] = 'Нет данных'
    try:
        capital = org['Уставный капитал (складочный капитал, уставный фонд, вклады товарищей) 2020 '] \
                  / org['БАЛАНС 2020 ']
        if capital > 0.2 or capital < 0.02:
            capital = 0
        else:
            capital = -120 * (capital - 0.11) ** 2 + 1
        org['sustainability'] = 0.35 * capital
        if org['Лицензии'] == 'Все лицензии':
            org['Лицензии'] = 0
        org['sustainability'] += 0.32 * scale(org['Лицензии'], 1, 3)
        try:
            trademark = org['Товарные знаки']
        except (ValueError, KeyError, TypeError):
            trademark = 0
        org['sustainability'] += 0.33 * scale(trademark, 1, 5)
        org['sustainability'] *= 10
    except (ValueError, KeyError, TypeError, ZeroDivisionError):
        org['sustainability'] = 'Нет данных'
    try:
        org['provider_experience'] = 0.5 * scale(org['provider'], 3, 10)
        org['provider_experience'] += 0.25 * scale(org['government_contracts_amount'], 0, 3)
        org['provider_experience'] += 0.25 * scale(org['government_contracts_total'], 100000, 1200000)
        org['provider_experience'] *= 10
    except (ValueError, KeyError, TypeError):
        org['provider_experience'] = 'Нет данных'
    org['experience_total'] = 0
    if org['size'] != 'Нет данных':
        org['experience_total'] += 0.2 * org['size']
    if org['stability'] != 'Нет данных':
        org['experience_total'] += 0.2 * org['stability']
    if org['sustainability'] != 'Нет данных':
        org['experience_total'] += 0.25 * org['sustainability']
    if org['provider_experience'] != 'Нет данных':
        org['experience_total'] += 0.35 * org['provider_experience']
    return org


def get_juridical_info(org) -> {}:
    """
    Юридические показатели организации по десятибалльной шкале
    """
    org['Tax behavior'] = 0
    if 'Положительный факт: Спецреестр ФНС (Имеющие задолженность по уплате налогов)' in org:
        org['Tax behavior'] += 0.25
    if 'Положительный факт: Спецреестр ФНС (Не представляющие налоговую отчетность более года)' in org:
        org['Tax behavior'] += 0.25
    if 'Положительный факт: Сведения о суммах недоимки и задолженности по пеням и штрафам' in org:
        org['Tax behavior'] += 0.25
    if 'Положительный факт: Наличие отчетности' in org:
        org['Tax behavior'] += 0.25
    org['Tax behavior'] *= 10
    org['Conscientiousness'] = 0
    if 'Положительный факт: Информационная открытость' in org:
        org['Conscientiousness'] = 10
    org['Director'] = 0
    if 'Положительный факт: Недостоверность данных о Руководителе' in org:
        org['Director'] += 0.45
    if 'Положительный факт: Проверка наличия Руководителя в реестре банкротств' in org:
        org['Director'] += 0.55
    org['Director'] *= 10
    try:
        org['courts_mark'] = max(0, min(org['courts'] / 20, 1)) * 10
    except (ValueError, KeyError, TypeError):
        org['courts_mark'] = 'Нет данных'
    org['juridical_total'] = 0
    if org['Tax behavior'] != 'Нет данных':
        org['juridical_total'] += 0.25 * org['Tax behavior']
    if org['Conscientiousness'] != 'Нет данных':
        org['juridical_total'] += 0.2 * org['Conscientiousness']
    if org['Director'] != 'Нет данных':
        org['juridical_total'] += 0.15 * org['Director']
    if org['courts_mark'] != 'Нет данных':
        org['juridical_total'] += 0.2 * org['courts_mark']
    return org


def get_property_status(org) -> {}:
    """
    Получение параметра, связанного со статусом имущества
    """
    changing_the_balance = (org['БАЛАНС 2020 '] - org['БАЛАНС 2019 ']) / org['БАЛАНС 2019 ']
    org['property status'] = 0.4 * scale(changing_the_balance, 0, 0.3)
    changing_the_profit = (org['Чистая прибыль (убыток) 2020 '] - org['Чистая прибыль (убыток) 2019 ']) \
                          / org['Чистая прибыль (убыток) 2019 ']
    org['property status'] += 0.4 * scale(changing_the_profit, 0, 0.3)
    growth_rate_ratio = org['Итого по разделу II 2020 '] - org['Итого по разделу II 2019 ']
    growth_rate_ratio /= org['Итого по разделу II 2019 ']
    growth_rate_ratio /= (org['Итого по разделу I 2020 '] - org['Итого по разделу I 2019 ']) \
                         / org['Итого по разделу I 2019 ']
    org['property status'] += 0.2 * scale(growth_rate_ratio, 0, 1.5)
    org['property status'] *= 10


def get_finance_info(org) -> {}:
    """
    Финансовые показатели организации по десятибалльной шкале
    """
    try:
        get_property_status(org)
    except (ValueError, KeyError, TypeError, ZeroDivisionError):
        org['property status'] = 'Нет данных'
    try:
        asset_turnover = 2 * org['Выручка 2020 '] / (org['БАЛАНС 2020 '] + org['БАЛАНС 2019 '])
        org['effectiveness'] = 0.4 * scale(asset_turnover, 0, 2)
        equity_capital = get_equity_capital(org)
        org['effectiveness'] += 0.6 * scale(org['Чистая прибыль (убыток) 2020 '] / equity_capital, 0.05, 0.3)
        org['effectiveness'] *= 10
    except (ValueError, KeyError, TypeError):
        org['effectiveness'] = 'Нет данных'
    try:
        equity_capital = get_equity_capital(org)
        financial_autonomy = 2 * equity_capital / (org['БАЛАНС 2020 '] + org['БАЛАНС 2019 '])
        if 0 <= financial_autonomy <= 1:
            financial_autonomy = -4 * (0.5 - financial_autonomy) ** 2 + 1
        else:
            financial_autonomy = 0
        org['financial condition'] = 0.3 * financial_autonomy
        maneuverability = (equity_capital - (org['Итого по разделу I 2020 '] +
                                             org['Итого по разделу I 2019 ']) / 2) / equity_capital
        if 0 <= maneuverability <= 0.7:
            maneuverability = -8 * (0.35 - maneuverability) ** 2 + 1
        else:
            maneuverability = 0
        org['financial condition'] += 0.2 * maneuverability
        liquidity = org['Финансовые вложения (за исключением денежных эквивалентов) 2020 '] \
                    + org['Финансовые вложения (за исключением денежных эквивалентов) 2019 ']
        liquidity += org['Денежные средства и денежные эквиваленты 2020 '] \
                     + org['Денежные средства и денежные эквиваленты 2019 ']
        liquidity /= org['Итого по разделу V 2020 '] + org['Итого по разделу V 2019 ']
        if 0.15 <= liquidity <= 0.55:
            liquidity = -25 * (0.35 - liquidity) ** 2 + 1
        else:
            liquidity = 0
        org['financial condition'] += 0.5 * liquidity
        org['financial condition'] *= 10
    except (ValueError, KeyError, TypeError):
        org['financial condition'] = 'Нет данных'
    org['finance_total'] = 0
    if org['property status'] != 'Нет данных':
        org['finance_total'] += 0.3 * org['property status']
    if org['effectiveness'] != 'Нет данных':
        org['finance_total'] += 0.3 * org['effectiveness']
    if org['financial condition'] != 'Нет данных':
        org['finance_total'] += 0.4 * org['financial condition']
    return org


def get_org_rating(org) -> {}:
    """
    Получение рейтинга организации и необходимых для него данных
    """
    org = get_finance_info(org)
    org = get_juridical_info(org)
    org = get_experience_info(org)
    org['rating'] = 0.5 * org['finance_total'] + 0.3 * org['juridical_total'] \
                    + 0.2 * org['experience_total']
    return org


async def all_data(inns):
    """
    Получение всей информации обо всех по списку инн
    """
    for inn in inns:
        orgs = get_all_info_by_inn(inn)
        for org in orgs:
            org = get_org_rating(org)
            yield org
