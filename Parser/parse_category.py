"""
Сбор всей информации по данной категории
"""

import time
import pickle
from honest_business import get_data_by_inn
from get_inns import get_inns


def parse_category(name) -> []:
    """
    Сбор данных о всех известных организациях в категории name
    """
    result = []
    inns = get_inns(name)
    counter = 0
    for inn in inns:
        time.sleep(3)
        result += get_data_by_inn(inn)
        if counter % 5 == 0:
            time.sleep(30)
            with open('data.pickle', 'wb') as file:
                pickle.dump(result, file)
        counter += 1
    with open('data/data.pickle', 'wb') as file:
        pickle.dump(result, file)
    return result

parse_category("metalware")

