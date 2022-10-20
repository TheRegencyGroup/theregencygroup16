/** @odoo-module **/

import { extendStore } from '@fe_owl_base/js/main';

const SHOPSITE_CATALOG_KEY = 'shopsite_catalog';

const shopsiteCatalogData = PRELOADED_DATA?.SHOPSITE_CATALOG_DATA;

if (shopsiteCatalogData) {
    class ShopsiteCatalogList {
        constructor() {
            for (let [key, value] of Object.entries(shopsiteCatalogData)) {
                this[key] = value;
            }
        }
    }

    extendStore({
            catalogList: new ShopsiteCatalogList()
        }
    )
}

export
{
    SHOPSITE_CATALOG_KEY,
}
