/** @odoo-module **/

import {mountComponentAsWidget, env} from "../base/main";
import {SHOPSITE_CATALOG_KEY} from "./store";

const {Component} = owl;
const {useStore} = owl.hooks;


class ShopsiteCatalogListComponent extends Component {

    constructor(...args) {
        super(...args);
        this.store = useStore(state => ({
            list: state[SHOPSITE_CATALOG_KEY],
        }), {
            store: env.store,
        });
    }


}

ShopsiteCatalogListComponent.template = 'shopsite_catalog_list';
mountComponentAsWidget('ShopsiteCatalogListComponent', ShopsiteCatalogListComponent).catch();
