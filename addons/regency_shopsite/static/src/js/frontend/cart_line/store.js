/** @odoo-module **/

import { extendStore } from '@fe_owl_base/js/main';

const countriesListData = PRELOADED_DATA?.COUNTRIES_DATA;
if (countriesListData) {
    class CountryWorldListData {
        constructor() {
            for (let [key, value] of Object.entries(countriesListData)) {
                this[key] = value;
            }
        }
    }

    extendStore({ key: 'countriesWorldData', obj: new CountryWorldListData })
}
