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

        async addOverlayToCart({ overlayTemplateId, attributeList, quantity, overlayProductId , overlayProductName }) {
            try {
                let params = {
                    qty: quantity,
                };
                if (!!overlayProductId) {
                    params = {
                        ...params,
                        overlay_product_id: overlayProductId,
                    };
                } else {
                    params = {
                        ...params,
                        overlay_template_id: overlayTemplateId,
                        attribute_list: attributeList,
                        overlay_product_name: overlayProductName,
                    };
                }
                let res = await rpc.query({
                    route: '/shopsite/cart/update_json',
                    params,
                });
                if (res) {
                    Object.assign(this, res);
                }

            } catch (e) {
                console.log(e)
            }
        }
    }

    extendStore({ key: 'cart', obj: new Cart })
}
