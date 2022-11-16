/** @odoo-module **/

import { mountComponentAsWidget } from '@fe_owl_base/js/main';
import rpc from 'web.rpc';
import Concurrency from 'web.concurrency';
import env from 'web.public_env';
import { useBus } from "@web/core/utils/hooks";

const { Component } = owl;
const dropPrevious = new Concurrency.MutexedDropPrevious();

export class DeliveryAddressCartLine extends Component {
    setup() {
        useBus(this.env.bus, 'delivery-addresses-data-changed', this.onChangedDeliveryAddressData.bind(this));
    }

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
        await dropPrevious.exec(() => {
            return rpc.query({
                route: '/shop/cart/add_new_address',
                params: {
                    sale_order_line_id,
                    address_name, // TODO REG-312 clarify and add other params
                },
            }).catch((e) => {
                alert(e.message?.data?.message || e.toString())
            });
        });
        env.bus.trigger('delivery-addresses-data-changed');
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

    async onChangedDeliveryAddressData() {
        let sale_order_line_id = this.solId;
        let deliveryAddressData  = await rpc.query({
                route: '/shop/cart/get_delivery_addresses_data',
                params: {
                    sale_order_line_id,
                },
            }).catch((e) => {
                alert(e.message?.data?.message || e.toString())
            });
        // updates props
        this.props.solData = JSON.parse(deliveryAddressData)
        this.render()

    }
}

DeliveryAddressCartLine.props = {
    solData: {
        type: Object,
    },
}
DeliveryAddressCartLine.template = 'address_cart_line';

mountComponentAsWidget('DeliveryAddressCartLine', DeliveryAddressCartLine).catch();
