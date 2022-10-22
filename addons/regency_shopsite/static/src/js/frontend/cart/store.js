/** @odoo-module **/

import { extendStore } from '@fe_owl_base/js/main';
import rpc from 'web.rpc';

const cartData = PRELOADED_DATA?.CART_DATA;
if (cartData) {
    class Cart {
        constructor() {
            for (let [key, value] of Object.entries(cartData)) {
                this[key] = value;
            }
        }

        async addToCart({ overlayTemplateId, attributeList, quantity}) {

        }
    }

    extendStore({ key: 'cart', obj: new Cart })
}
