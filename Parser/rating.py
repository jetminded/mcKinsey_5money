from org_by_inn import get_all_info_by_inn


# заглушка по получению рейтинга
def get_org_rating(org) -> int:
    return 10


# получение всей инфы обо всех
async def all_data(inns):
    for inn in inns:
        orgs = get_all_info_by_inn(inn)
        for org in orgs:
            org['our_rating'] = get_org_rating(org)
            yield org
