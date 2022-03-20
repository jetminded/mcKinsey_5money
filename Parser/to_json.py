"""
Преобразование сохраненного pickle файла в формат JSON
"""

import pickle
import json
from rating import get_juridical_info, get_experience_info, get_finance_info


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


with open('data/rubber_data.pickle', 'rb') as f:
    data = pickle.load(f)
print(len(data))
data = convert_to_dict(data)
c = 0
for el in data:
    if el['status'] == 'Действующее' and el["Реестр недобросовестных поставщиков"] == "Не числится":
        el = get_finance_info(el)
        el = get_experience_info(el)
        el = get_juridical_info(el)
        el['rating'] = 0.5 * el['finance_total'] + 0.3 * el['juridical_total'] \
                   + 0.2 * el['experience_total']
    else:
        c += 1
print(c)

# with open("rubber_data_file.json", "w") as write_file:
#     json.dump(data, write_file, ensure_ascii=False)
