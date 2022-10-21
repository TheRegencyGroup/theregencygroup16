/** @odoo-module **/
import "./store";
import { mountComponentAsWidget } from "@fe_owl_base/js/main";

const { Component, onPatched } = owl;
import { useStore } from "@fe_owl_base/js/main";
import { ListPaginationComponent } from "../list_pagination/list_pagination";


export class ShopsiteCatalogListComponent extends Component {
    setup() {
        onPatched(this.onPatched.bind(this))
        this.store = useStore();
        this.limit = this.store.catalogList.limit;
        this.count = this.store.catalogList.count;
        this.updateList = this.store.catalogList.updateShopsiteCatalogList;

    }

    get itemList() {
        return this.store.catalogList.data || [];
    }

    get itemModel() {
        return this.store.catalogList.model;
    }

    get currentPage() {
        return this.store.catalogList.page;
    }

    onPatched() {
        console.log(this.productList)
    }
    updateShopsiteItemsList (){
        this.updateList(1, 'overlay.template')
    }

    updateShopsiteProductsList (){
        this.updateList(1, 'overlay.product')
    }
}

// ShopsiteCatalogListComponent.components = {
//     // ListPaginationComponent,
// }
ShopsiteCatalogListComponent.template = 'shopsite_catalog_list';
mountComponentAsWidget('ShopsiteCatalogListComponent', ShopsiteCatalogListComponent).catch();
