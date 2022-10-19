/** @odoo-module **/

import {addStore} from '../base/main';

const SHOPSITE_CATALOG_KEY = 'shopsite_catalog';

const shopsiteCatalogData = PRELOADED_DATA.SHOPSITE_CATALOG_DATA;
if (shopsiteCatalogData) {
    const actions = {};
    const state = {
        [SHOPSITE_CATALOG_KEY]: shopsiteCatalogData,
    };
    addStore(actions, state);
}

export {
    SHOPSITE_CATALOG_KEY,
}
