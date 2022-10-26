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

        async addOverlayToCart({ overlayTemplateId, attributeList, quantity, overlayProductId , overlayProductName, overlayAreaList, previewImagesData }) {
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
                        overlay_area_list: overlayAreaList,
                        preview_images_data: previewImagesData,
                    };
                }
                let res = await rpc.query({
                    route: '/shop/cart/update_json/overlay',
                    params,
                });
                if (res && res.cartData) {
                    Object.assign(this, res.cartData);
                }
                if (res && res.overlayProductData) {
                    return res.overlayProductData;
                }
                return false;
            } catch (e) {
                alert(e.message?.data?.message || e.toString());
            }
        }
    }

    extendStore({ key: 'cart', obj: new Cart })
}
