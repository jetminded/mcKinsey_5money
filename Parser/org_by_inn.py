# получение всей информации о всех предприятиях по данному inn

from honest_business import get_data_by_inn


def convert_to_dict(inp):
    result = []
    for ar in inp:
        obj = {}
        for field in ar:
            try:
                if field[1].find('▒') > -1:
                    field[1] = '-'
            except:
                pass
            try:
                value = field[1].replace(' ', '')
                value = value.replace(',', '.')
                if float(value).is_integer():
                    obj[field[0]] = int(float(value))
                else:
                    obj[field[0]] = float(value)
            except:
                obj[field[0]] = field[1]
        result.append(obj)
    return result


# возвращает массив словарей
def get_all_info_by_inn(inn) -> []:
    return convert_to_dict(get_data_by_inn(inn))
