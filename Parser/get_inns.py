# Получение ИНН по категории, можно читать из файла, можно спарсить

from b2b import get_inns_by_category


def get_inns_from_file(filename):
    inns = []
    f = open(filename, 'r')
    for line in f:
        inns.append(int(line))
    return inns


def get_inns(category, mode='file', offset=0) -> []:
    if mode == 'file':
        return get_inns_from_file(category + ".txt")
    return get_inns_by_category(category, offset)
