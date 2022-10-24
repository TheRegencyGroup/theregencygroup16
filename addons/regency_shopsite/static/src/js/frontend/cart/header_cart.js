/** @odoo-module **/

import './store';
import { mountComponentAsWidget, useStore } from '@fe_owl_base/js/main';
import { OverlayTemplatePageComponent } from "../overlay_template_page/overlay_template_page";

const { Component } = owl;

export class HeaderCart extends Component {
    setup() {
        this.store = useStore();
    }

    get cartItemsNumber() {
        return this.store.cart.lineList.length;
    };
}

HeaderCart.template = 'header_cart';

mountComponentAsWidget('HeaderCart', HeaderCart).catch();
