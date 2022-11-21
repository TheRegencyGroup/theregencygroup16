/** @odoo-module **/

import { mountComponentAsWidget } from '@fe_owl_base/js/main';
import { DeliveryAddressCartLine } from './cart_line_adress_selector'
import core from 'web.core'

import { WebsiteSale } from 'website_sale.website_sale';

WebsiteSale.include({
    init: function () {
        this._super.apply(this, arguments);
        core.bus.on('cart_amount_changed', this, () => mountComponentAsWidget('DeliveryAddressCartLine', DeliveryAddressCartLine).catch()
    )
    },
});
