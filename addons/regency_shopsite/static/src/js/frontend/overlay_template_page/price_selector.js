/** @odoo-module **/

import { useStore } from '@fe_owl_base/js/main';

const { Component } = owl;

export class PriceSelector extends Component {
    setup() {
        this.store = useStore();
    }

    get priceList() {
        return Object.values(this.store.otPage.priceList);
    };

    formatPrice(price) {
        return `$${price.toFixed(2)}`
    }

    onChangePrice(priceId) {
        this.store.otPage.changeSelectedPrice(priceId);
    }
}

PriceSelector.template = 'overlay_template_page_price_selector';
