/** @odoo-module **/
import { extendStore } from '@fe_owl_base/js/main';
import rpc from 'web.rpc';

const shopsiteCatalogData = PRELOADED_DATA?.SHOPSITE_CATALOG_DATA;

if (shopsiteCatalogData) {
    class ShopsiteCatalogList {
        constructor() {
            for (let [key, value] of Object.entries(shopsiteCatalogData)) {
                this[key] = value;
            }
        }

        async updateShopsiteCatalogList(page, model) {
            try {
                let data = await rpc.query({
                    route: '/shop/list_update',
                    params: {
                        page: page,
                        model: model,
                    },
                });
                console.log(data.data.length);
                this.data = data.data;
                this.page = page;
                this.count = data.count;
                this.model = model;
            } catch (e) {
                throw(e);
            }
        }
    }

    extendStore({ key: 'catalogList', obj: new ShopsiteCatalogList() })
}

