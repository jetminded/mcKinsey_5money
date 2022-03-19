"""
Получение всей информации об организации и ее преобразование в словарь
"""
from honest_business import get_data_by_inn
from to_json import convert_to_dict


def get_all_info_by_inn(inn) -> []:
    """
    Получение всей информации об организации и ее преобразование в словарь
    """
    return convert_to_dict(get_data_by_inn(inn))
