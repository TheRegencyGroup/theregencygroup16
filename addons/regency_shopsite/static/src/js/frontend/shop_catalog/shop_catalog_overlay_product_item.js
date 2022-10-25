/** @odoo-module **/

import "./store";
import { useStore } from "@fe_owl_base/js/main";

const { Component } = owl;
const DATE_FORMAT_OPTIONS = { year: 'numeric', month: 'short', day: 'numeric' };

export class ShopCatalogOverlayProductItem extends Component {

    get item() {
        return this.props.itemData;
    }

    get dateStrInUserTZ() {
        let date = this.item.lastUpdatedDate;
        if (date) {
            return new Date(date).toLocaleDateString("en-US", DATE_FORMAT_OPTIONS);
        }
        return '';
    }

    get lastUpdatedDescription() {
        let name = this.item.updatedByName;
        let date = this.dateStrInUserTZ;
        let separator = (name && date) ? ', ' : '';
        if (name || date) {
            name = name ? `by ${name}` : '';
            return `Updated ${date}${separator}${name}`;
        }
        return '';
    }
}

ShopCatalogOverlayProductItem.props = {
    itemData: Object,
};

ShopCatalogOverlayProductItem.template = 'shop_catalog_overlay_product_item';
