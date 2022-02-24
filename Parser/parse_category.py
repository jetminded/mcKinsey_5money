from b2b import get_inns_by_category
from honest_business import get_data_by_inn


def parse_category(name):
    result = []
    inns = get_inns_by_category(name)
    print(inns)
    for inn in inns:
        result += get_data_by_inn(inn)
    return result


print(parse_category(""))
