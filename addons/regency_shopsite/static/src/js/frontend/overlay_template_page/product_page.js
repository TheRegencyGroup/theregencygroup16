/** @odoo-module **/

import {registry, Widget} from 'web.public.widget';
import legacyEnv from "web.public_env";
import {cartHandlerMixin, animateClone, updateCartNavBar} from 'website_sale.utils';

registry.ToggleOverlayEditor = Widget.extend({
    selector: '.toggle_product_overlay_editor_buttons',

    events: {
        'click button': 'onClickButton',
    },

    onClickButton (event) {
        let btn = event.target;
        let showEditor = false
        if (btn.classList.contains('toggle_product_overlay_gallery')) {
            showEditor = true;
        }
        this.el.querySelector('.toggle_product_overlay_editor').classList.toggle('d-none', !showEditor);
        this.el.querySelector('.toggle_product_overlay_gallery').classList.toggle('d-none', showEditor);
        document.querySelector('.product_overlay_editor').classList.toggle('d-none', showEditor);
        document.querySelector('.product_gallery').classList.toggle('d-none', !showEditor);
    },
});

registry.RegencyChangeProductAttribute = Widget.extend({
    selector: '.js_add_cart_variants',

    events: {
        'change li[data-attribute_name="Overlay"] .custom-radio input': '_onChangeOverlay',
        'change li[data-attribute_name="color"] .custom-radio input': '_onChangeColor',
        'change li[data-attribute_name="Color"] .custom-radio input': '_onChangeColor',
    },

    _onChangeOverlay (event) {
        legacyEnv.bus.trigger('change-overlay-attribute-value-id', parseInt(event.target.dataset.value_id));
    },

    _onChangeColor (event) {
        legacyEnv.bus.trigger('change-color-attribute-value-id', parseInt(event.target.dataset.regencyValueId));
    },
});

cartHandlerMixin._addToCartInPage = function (params) {
    let inputs = document.querySelectorAll(`input[data-attribute_name='Overlay']`);
    let checkedInput = Array.from(inputs).find(e => !!e.checked);
    if (checkedInput) {
        let customValueInput = document.querySelector(`li[data-attribute_name='Overlay'] .variant_custom_value`);
        if (customValueInput) {
            let product_custom_attribute_values = JSON.parse(params.product_custom_attribute_values);
            let overlayAttribute = product_custom_attribute_values
                .find(e => e.custom_product_template_attribute_value_id === parseInt(checkedInput.dataset.value_id));
            if (overlayAttribute) {
                overlayAttribute.custom_value = `${legacyEnv.session.user_id}_${new Date().valueOf()}`;
                params.product_custom_attribute_values = JSON.stringify(product_custom_attribute_values);
            }
        }
        legacyEnv.bus.trigger('get-image-with-overlay',
            parseInt(checkedInput.dataset.value_id),
            (data) => {
                if (data) {
                    params = Object.assign(params, {
                        'images_with_overlay': data,
                    });
                }
                addToCart(this, params);
            });
    } else {
        addToCart(this, params);
    }
}

function addToCart(ctx, params) {
    params.force_create = true;
    return ctx._rpc({
        route: "/shop/cart/update_json",
        params: params,
    }).then(async data => {
        if (data.cart_quantity && (data.cart_quantity !== parseInt($(".my_cart_quantity").text()))) {
            await animateClone($('header .o_wsale_my_cart').first(), ctx.$itemImgContainer, 25, 40);
            updateCartNavBar(data);
        }
    });
}
