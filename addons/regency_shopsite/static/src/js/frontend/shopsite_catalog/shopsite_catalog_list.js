/** @odoo-module **/

import { mountComponentAsWidget } from "@fe_owl_base/js/main";

const { Component } = owl;
import { useStore, useState } from "@fe_owl_base/js/main";


export class ShopsiteCatalogListComponent extends Component {
    setup() {
        this.store = useStore();
        this.list = this.store.catalogList.data
    }

    get productList() {
            return this.list || [];
        }
}

ShopsiteCatalogListComponent.template = 'shopsite_catalog_list';
mountComponentAsWidget('ShopsiteCatalogListComponent', ShopsiteCatalogListComponent).catch();
