/** @odoo-module **/
import "./store";
import { mountComponentAsWidget } from "@fe_owl_base/js/main";
const { useState } = owl

const { Component } = owl;
import { useStore } from "@fe_owl_base/js/main";
import { ListPaginationComponent } from "../list_pagination/list_pagination";


export class ShopsiteCatalogListComponent extends Component {
    setup() {
        this.store = useStore();
    }

    get itemList() {
        return this.store.catalogData.data || [];
    }

    get itemModel() {
        return this.store.catalogData.model;
    }

    get currentPage() {
        return this.store.catalogData.page;
    }

    updateShopsiteItemsList (){
        this.store.catalogData.updateListData(1, 'overlay.template')
    }

    updateShopsiteProductsList (){
        this.store.catalogData.updateListData(1, 'overlay.product')
    }
}

// ShopsiteCatalogListComponent.components = {
//     // ListPaginationComponent,
// }
ShopsiteCatalogListComponent.template = 'shopsite_catalog_list';
mountComponentAsWidget('ShopsiteCatalogListComponent', ShopsiteCatalogListComponent).catch();
