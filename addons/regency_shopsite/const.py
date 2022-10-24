OVERLAY_PRODUCT_ID_URL_PARAMETER = 'op'

PAGE_URL_PARAMETER = 'page'
SHOP_CATALOG_TAB_URL_PARAMETER = 'tab'

OVERLAY_TEMPLATE_CATALOG_TAB_KEY = 'ot'
OVERLAY_PRODUCT_CATALOG_TAB_KEY = 'op'

SHOP_CATALOG_ITEM_LIMIT = 6

DEFAULT_OVERLAY_TEMPLATE_CATALOG_SORT_FIELD = 'name'
DEFAULT_OVERLAY_TEMPLATE_CATALOG_SORT_DIR = 'asc'
DEFAULT_OVERLAY_PRODUCT_CATALOG_SORT_FIELD = 'name'
DEFAULT_OVERLAY_PRODUCT_CATALOG_SORT_DIR = 'asc'

DEFAULT_SHOP_CATALOG_TAB_SORT = {
    OVERLAY_TEMPLATE_CATALOG_TAB_KEY: f'{DEFAULT_OVERLAY_TEMPLATE_CATALOG_SORT_FIELD} {DEFAULT_OVERLAY_TEMPLATE_CATALOG_SORT_DIR}',
    OVERLAY_PRODUCT_CATALOG_TAB_KEY: f'{DEFAULT_OVERLAY_PRODUCT_CATALOG_SORT_FIELD} {DEFAULT_OVERLAY_PRODUCT_CATALOG_SORT_DIR}',
}

SHOP_CATALOG_TAB_MODELS = {
    OVERLAY_TEMPLATE_CATALOG_TAB_KEY: 'overlay.template',
    OVERLAY_PRODUCT_CATALOG_TAB_KEY: 'overlay.product',
}