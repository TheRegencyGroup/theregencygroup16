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
            this.addingToCart = false;
        }

        async addOverlayToCart({
                                   overlayTemplateId,
                                   attributeList,
                                   quantity,
                                   overlayProductId,
                                   overlayProductName,
                                   overlayAreaList,
                                   previewImagesData,
                                   overlayProductWasChanged,
        }) {
            this.addingToCart = true;
            let data = false;
            try {
                let params = {
                    qty: quantity,
                };
                if (!!overlayProductId) {
                    params = {
                        ...params,
                        overlay_product_id: overlayProductId,
                    };
                }
                if (!overlayProductId || overlayProductWasChanged) {
                    params = {
                        ...params,
                        overlay_template_id: overlayTemplateId,
                        attribute_list: attributeList,
                        overlay_product_name: overlayProductName,
                        overlay_area_list: overlayAreaList,
                        preview_images_data: previewImagesData,
                        overlay_product_was_changed: overlayProductWasChanged,
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
                    data = res.overlayProductData;
                }
            } catch (e) {
                alert(e.message?.data?.message || e.toString());
            }
            this.addingToCart = false;
            return data;
        }
    }

    extendStore({ key: 'cart', obj: new Cart })
}
