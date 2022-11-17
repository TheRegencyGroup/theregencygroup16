/** @odoo-module **/

import { mountComponentAsWidget } from '@fe_owl_base/js/main';
import rpc from 'web.rpc';
import Concurrency from 'web.concurrency';
import env from 'web.public_env';

const { Component, useState, useRef} = owl;
const dropPrevious = new Concurrency.MutexedDropPrevious();

export class DeliveryAddressCartLine extends Component {
    setup() {
        this.newAddressInputEls = {
            name: useRef('new_address_name_input'),
        }
        this.state = useState({
            showModal: false,
        });
        env.bus.on('delivery-addresses-data-changed', null, this.onChangedDeliveryAddressData.bind(this));
    }

    get solId() { // 'sol' means 'sale order line'
        return this.props.solData.solId
    }

    get currentDeliveryAddress() {
        return this.props.solData.currentDeliveryAddress
    }

    get possibleDeliveryAddresses() {
        return this.props.solData.possibleDeliveryAddresses
    }

    hideInputFormModal() {
        this.state.showModal = false;
    }

    async processDeliveryAddressChanging(ev) {
        let selectionTagVal = ev.target.value
        if (selectionTagVal === 'add_new_address') {
            this.state.showModal = true
            // let address_name = 'Some Address Name' // TODO REG-312
            // await this.createNewDeliveryAddress(address_name);
        } else {
            await this.saveDeliveryAddress(selectionTagVal);
        }
    }

    async createNewDeliveryAddress() {
        let sale_order_line_id = this.solId
        let address_name = this.newAddressInputEls.name.el.value
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
        this.hideInputFormModal()

    }
}

DeliveryAddressCartLine.props = {
    solData: {
        type: Object,
    },
}
DeliveryAddressCartLine.template = 'address_cart_line';

mountComponentAsWidget('DeliveryAddressCartLine', DeliveryAddressCartLine).catch();
