"""
Получение всей информации об организации и ее преобразование в словарь
"""
from honest_business import get_data_by_inn


def convert_to_dict(inp):
    """
    Функция, преобразующая список с словарь, чтобы удобнее было конвертировать в JSON
    """
    result = []
    for element in inp:
        obj = {}
        for field in element:
            try:
                if field[1].find('▒') > -1:
                    field[1] = '-'
            except AttributeError:
                pass
            try:
                value = field[1].replace(' ', '')
                value = value.replace(',', '.')
                if float(value).is_integer():
                    obj[field[0]] = int(float(value))
                else:
                    obj[field[0]] = float(value)
            except (ValueError, AttributeError):
                obj[field[0]] = field[1]
        result.append(obj)
    return result


def get_all_info_by_inn(inn) -> []:
    """
    Получение всей информации об организации и ее преобразование в словарь
    """
    return convert_to_dict(get_data_by_inn(inn))
