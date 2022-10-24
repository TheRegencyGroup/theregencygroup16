/** @odoo-module **/
import { extendStore } from '@fe_owl_base/js/main';
import rpc from 'web.rpc';

const shopCatalogData = PRELOADED_DATA?.SHOP_CATALOG_DATA;

if (shopCatalogData) {
    class ShopCatalog {
        constructor() {
            for (let [key, value] of Object.entries(shopCatalogData)) {
                let _key = '_' + key;
                this[_key] = value;
                Object.defineProperty(this, key, {
                    get() {
                        return this[_key];
                    },
                    set() {
                        throw new Error("Use action to change store values");
                    }
                });
            }
            this._updateUrlParameters();
        }

        _updateUrlParameters() {
            let url = new URL(window.location.href);
            for (let [valueKey, paramKey] of Object.entries(this._urlParameterList)) {
                url.searchParams.set(paramKey, this[valueKey]);
            }
            window.history.replaceState(null, null, url);
        }

        async updateList({ page, limit, tab }) {
            page = page || this._currentPage;
            limit = limit || this._itemsLimit;
            tab = tab || this._currentTab;

            try {
                let res = await rpc.query({
                    route: '/shop/data',
                    params: {
                        page,
                        limit,
                        catalog_tab: tab,
                    },
                });
                if (res) {
                    res = Object.entries(res).reduce((a, e) => ({
                        ...a,
                        ['_' + e[0]]: e[1],
                    }), {});
                    Object.assign(this, res);
                    this._updateUrlParameters();
                }
            } catch (e) {
                console.log(e)
            }
        }
    }
    extendStore({ key: 'shopCatalog', obj: new ShopCatalog() })
}

