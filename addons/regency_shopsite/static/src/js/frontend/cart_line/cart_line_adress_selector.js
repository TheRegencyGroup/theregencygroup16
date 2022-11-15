/** @odoo-module **/

import { mountComponentAsWidget } from '@fe_owl_base/js/main';
import rpc from 'web.rpc';

const { Component, onMounted } = owl;

export class DeliveryAddressCartLine extends Component {

    get solId() {
        return this.props.solData.solId
    }

    get currentDeliveryAddress() {
        return this.props.solData.currentDeliveryAddress
    }

    get possibleDeliveryAddresses() {
        return this.props.solData.possibleDeliveryAddresses
    }

    async saveDeliveryAddress(ev) {
        let sale_order_line_id = this.solId
        let delivery_address_id = ev.target.value
        delivery_address_id = (
            delivery_address_id && (typeof delivery_address_id === 'string' || typeof delivery_address_id === 'number')
        ) ? Number(delivery_address_id) : false
        try {
            let res = await rpc.query({
                route: '/shop/cart/save_delivery_address',
                params: {
                    sale_order_line_id,
                    delivery_address_id,
                },
            });
        } catch (e) {
            alert(e.message?.data?.message || e.toString())
        }
    }
}

DeliveryAddressCartLine.props = {
    solData: {
        type: Object,
    },
}
DeliveryAddressCartLine.template = 'address_cart_line';

mountComponentAsWidget('DeliveryAddressCartLine', DeliveryAddressCartLine).catch();
