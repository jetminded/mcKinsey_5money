import time

from b2b import get_inns_by_category
from honest_business import get_data_by_inn
import pickle


def parse_category(name):
    result = []
    inns = get_inns_by_category(name)
    print(inns)
    for i in range(len(inns)):
        time.sleep(2)
        result += get_data_by_inn(inns[i])
        if i % 5 == 0:
            with open('data.pickle', 'wb') as f:
                pickle.dump(result, f)

    return result


print(parse_category(""))
