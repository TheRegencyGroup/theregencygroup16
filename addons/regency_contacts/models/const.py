import re

SPLIT_REGEX = re.compile(r"[\s_]+")


def readable_name(name: str) -> str:
    return " ".join(y for y in SPLIT_REGEX.split(name.lower())).capitalize()


REBATE_COMPANY = 'rebate_company'
PARTNER_COMPANY = 'partner_company'
HOTEL_BRAND = 'hotel_brand'
HOTEL_GROUP = 'hotel_group'
MANAGEMENT_GROUP = 'management_group'
HOTEL = 'hotel'
CONTACT = 'contact'

ENTITIES = (
    REBATE_COMPANY,
    PARTNER_COMPANY,
    HOTEL_BRAND,
    HOTEL_GROUP,
    MANAGEMENT_GROUP,
    HOTEL,
    CONTACT,
)

ENTITY_SELECTION = [(x, readable_name(x)) for x in ENTITIES]
