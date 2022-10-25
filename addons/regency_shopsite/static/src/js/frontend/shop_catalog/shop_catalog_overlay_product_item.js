/** @odoo-module **/

import "./store";
import { useStore } from "@fe_owl_base/js/main";

const { Component } = owl;

export class ShopCatalogOverlayProductItem extends Component {
    setup() {
        this.dateOptions = { year: 'numeric', month: 'short', day: 'numeric' };
        this.item.description = this.description;
    }

    get item() {
        return this.props.itemData;
    }

    get dateStrInUserTZ() {
        let date = this.item.lastUpdatedDate;
        if (date) {
            return new Date(date).toLocaleDateString("en-US", this.dateOptions);
        }
        return '';
    }

    get description() {
        let name = `by ${this.item.updatedByName}`;
        let date = this.dateStrInUserTZ;
        let separator = (name && date) ? ', ' : '';
        if (name || date) {
            return `Updated ${date}${separator}${name}`;
        }
        return '';
    }
}

ShopCatalogOverlayProductItem.props = {
    itemData: Object,
};

ShopCatalogOverlayProductItem.template = 'shop_catalog_overlay_product_item';
