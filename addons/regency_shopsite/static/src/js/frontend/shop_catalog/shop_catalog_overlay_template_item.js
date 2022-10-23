/** @odoo-module **/

import "./store";

const { Component } = owl;

export class ShopCatalogOverlayTemplateItem extends Component {
    get item() {
        return this.props.itemData;
    }
}

ShopCatalogOverlayTemplateItem.props = {
    itemData: Object,
};

ShopCatalogOverlayTemplateItem.template = 'shop_catalog_overlay_template_item';
