"""
Получение ИНН по категории, можно читать из файла, можно спарсить, начиная с определенной страницы
"""

from b2b import get_inns_by_category


def get_inns_from_file(filename) -> []:
    """
    Чтение инн из файла
    """
    inns = []
    f = open(filename, 'r')
    for line in f:
        inns.append(int(line))
    return inns


def get_inns(category, mode='file', offset=0) -> []:
    """
    Получение списка инн поставщиков данной категории
    Возможно чтение из файла или сбор данных, начиная с заданной offset'ом страницы
    """
    if mode == 'file':
        return get_inns_from_file("data/" + category + ".txt")
    return get_inns_by_category(category, offset)
