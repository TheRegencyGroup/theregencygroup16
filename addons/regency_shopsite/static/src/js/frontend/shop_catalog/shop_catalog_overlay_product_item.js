/** @odoo-module **/

import "./store";
import { useStore } from "@fe_owl_base/js/main";

const { Component } = owl;

export class ShopCatalogOverlayProductItem extends Component {
    get item() {
        return this.props.itemData;
    }
}

ShopCatalogOverlayProductItem.props = {
    itemData: Object,
};

ShopCatalogOverlayProductItem.template = 'shop_catalog_overlay_product_item';
