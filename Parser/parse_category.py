import time
from honest_business import get_data_by_inn
import pickle


def get_inns_from_file(filename):
    inns = []
    f = open(filename, 'r')
    for line in f:
        inns.append(int(line))
    return inns


def parse_category(name):
    result = []
    inns = get_inns_from_file("metalware.txt")
    for i in range(len(inns)):
        print(i)
        time.sleep(2)
        result += get_data_by_inn(inns[i])
        if i % 5 == 0:
            with open('data.pickle', 'wb') as f:
                pickle.dump(result, f)
    with open('data.pickle', 'wb') as f:
        pickle.dump(result, f)
    return result


print(len(parse_category("")))
