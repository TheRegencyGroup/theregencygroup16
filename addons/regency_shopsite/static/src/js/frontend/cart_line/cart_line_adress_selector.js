/** @odoo-module **/

import { mountComponentAsWidget } from '@fe_owl_base/js/main';
import rpc from 'web.rpc';
import Concurrency from 'web.concurrency';

const { Component } = owl;
const dropPrevious = new Concurrency.MutexedDropPrevious();

export class DeliveryAddressCartLine extends Component {

    get solId() { // 'sol' = 'sale order line'
        return this.props.solData.solId
    }

    get currentDeliveryAddress() {
        return this.props.solData.currentDeliveryAddress
    }

    get possibleDeliveryAddresses() {
        return this.props.solData.possibleDeliveryAddresses
    }

    async processDeliveryAddressChanging(ev) {
        let selectionTagVal = ev.target.value
        if (selectionTagVal === 'add_new_address') {
            let address_name = 'Some Address Name' // TODO REG-312
            await this.createNewDeliveryAddress(address_name);
        } else {
            await this.saveDeliveryAddress(selectionTagVal);
        }
    }

    async createNewDeliveryAddress(address_name) {
        let sale_order_line_id = this.solId
        dropPrevious.exec(() => {
            return rpc.query({
                route: '/shop/cart/add_new_address',
                params: {
                    sale_order_line_id,
                    address_name, // TODO REG-312 clarify and add other params
                },
            }).catch((e) => {
                alert(e.message?.data?.message || e.toString())
            })
        })
    }

    async saveDeliveryAddress(deliveryAddressId) {
        let sale_order_line_id = this.solId
        let delivery_address_id = (
            deliveryAddressId && (typeof deliveryAddressId === 'string' || typeof deliveryAddressId === 'number')
        ) ? Number(deliveryAddressId) : false;
        dropPrevious.exec(() => {
            return rpc.query({
                route: '/shop/cart/save_delivery_address',
                params: {
                    sale_order_line_id,
                    delivery_address_id,
                },
            }).catch((e) => {
                alert(e.message?.data?.message || e.toString())
            })
        })
    }
}

DeliveryAddressCartLine.props = {
    solData: {
        type: Object,
    },
}
DeliveryAddressCartLine.template = 'address_cart_line';

mountComponentAsWidget('DeliveryAddressCartLine', DeliveryAddressCartLine).catch();
