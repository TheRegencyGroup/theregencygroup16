/** @odoo-module **/
import { extendStore } from '@fe_owl_base/js/main';
import rpc from 'web.rpc';

const shopsiteCatalogData = PRELOADED_DATA?.SHOPSITE_CATALOG_DATA;

if (shopsiteCatalogData) {
    class ShopsiteCatalogListData {
        constructor() {
            for (let [key, value] of Object.entries(shopsiteCatalogData)) {
                this[key] = value;
            }
            this.numberOfPages = this.calcNumberOfPages()
        }

        async updateListData(page, model) {
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
                this.limit = data.limit
                this.numberOfPages = this.calcNumberOfPages()
                console.log(this.numberOfPages);
            } catch (e) {
                throw(e);
            }
        }

        calcNumberOfPages() {
        let listCount = this.count;
        let listLimit = this.limit;
        let numbers = Math.floor(listCount / listLimit);
        if (listCount % listLimit > 0) {
            numbers++;
        }
        return numbers;
    }

    }
    extendStore({ key: 'catalogData', obj: new ShopsiteCatalogListData() })
}

