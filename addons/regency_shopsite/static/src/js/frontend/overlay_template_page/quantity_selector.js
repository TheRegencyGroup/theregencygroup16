/** @odoo-module **/

import { useStore } from '@fe_owl_base/js/main';

const { Component, useRef } = owl;

export class QuantitySelector extends Component {
    setup() {
        this.store = useStore();

        this.quantityInputRef = useRef('quantity_input');
    }

    get priceList() {
        return Object.values(this.store.otPage.priceList);
    };

    get invalidQuantity() {
        return this.store.otPage.quantity < this.store.otPage.minimumOrderQuantity;
    }

    get totalPrice() {
        const price = this.store.otPage.selectedPrice.price;
        const qty = this.store.otPage.quantity;
        return this.formatPrice(price * qty);
    }

    formatPrice(price) {
        return `$${price.toFixed(2)}`
    }

    onChangePrice(priceId) {
        if (priceId === this.store.otPage.selectedPriceId) {
            return
        }
        this.store.otPage.changeSelectedPrice(priceId);
    }

    changeQuantity() {
        let qty = this.quantityInputRef.el.value;
        if (qty) {
            qty = parseInt(qty);
        } else {
            qty = this.store.otPage.minimumOrderQuantity;
            this.quantityInputRef.el.value = qty;
        }
        this.prevInputQuantityValue = qty;
        this.store.otPage.changeQuantity(qty);
    }

    onInputQuantity() {
        if (!this.prevInputQuantityValue) {
            this.prevInputQuantityValue = this.store.otPage.quantity;
        }
        if (!this.quantityInputRef.el.validity.valid) {
            this.quantityInputRef.el.value = this.prevInputQuantityValue;
        } else {
            this.prevInputQuantityValue = this.quantityInputRef.el.value;
        }
    }

    onChangeQuantity() {
        this.changeQuantity();
    }

    onKeypressQuantity(event) {
        if (event.key === 'Enter') {
            this.changeQuantity();
            this.quantityInputRef.el.blur();
        }
    }
}

QuantitySelector.template = 'overlay_template_page_quantity_selector';
