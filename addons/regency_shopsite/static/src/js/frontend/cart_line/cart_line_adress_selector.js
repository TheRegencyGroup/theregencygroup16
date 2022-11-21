/** @odoo-module **/

import { mountComponentAsWidget, useStore } from '@fe_owl_base/js/main';
import rpc from 'web.rpc';
import Concurrency from 'web.concurrency';
import env from 'web.public_env';

const { Component, useState, useRef} = owl;
const dropPrevious = new Concurrency.MutexedDropPrevious();

export class DeliveryAddressCartLine extends Component {
    setup() {
        this.newAddressInputEls = {
            name: useRef('new_address_name_input'),
            street: useRef('new_address_street_input'),
            street2: useRef('new_address_street2_input'),
            city: useRef('new_address_city_input'),
            zip: useRef('new_address_zip_input'),
            province: useRef('new_address_province_input'),
            country: useRef('new_address_country_input'),
        };
        this.store = useStore();
        this.provinceList = this.store.countriesWorldData.provinceList;
        this.countryList = this.store.countriesWorldData.countryList;
        this.state = useState({
            showModal: false,
            currentCountryId: this.store.countriesWorldData.defaultCountryId,
            currentCountryHasProvinces: this.store.countriesWorldData.defaultCountryHasProvince,
        });
        env.bus.on('delivery-addresses-data-changed', null, this.onChangedDeliveryAddressData.bind(this));
    }

    get solId() { // 'sol' means 'sale order line'
        return this.props.solData.solId;
    }

    get currentDeliveryAddress() {
        return this.props.solData.currentDeliveryAddress;
    }

    get possibleDeliveryAddresses() {
        return this.props.solData.possibleDeliveryAddresses;
    }

    hideInputFormModal() {
        this.state.showModal = false;
    }
    displayInputFormModal() {
        this.state.showModal = true;
    }

    async processDeliveryAddressChanging(ev) {
        let selectionTagVal = ev.target.value;
        if (selectionTagVal === 'add_new_address') {
            this.displayInputFormModal();
        } else {
            await this.saveDeliveryAddress(selectionTagVal);
        }
    }

    async createNewDeliveryAddress() {
        let addressParams = this.getParamsForAddressCreation()
        await dropPrevious.exec(() => {
            return rpc.query({
                route: '/shop/cart/add_new_address',
                params: {
                    ...addressParams
                },
            }).catch((e) => {
                alert(e.message?.data?.message || e.toString());
            });
        });
        env.bus.trigger('delivery-addresses-data-changed');
    }

    getParamsForAddressCreation(){
        return {
            sale_order_line_id: this.solId,
            address_name: this.newAddressInputEls.name.el.value,
            street: this.newAddressInputEls.street.el.value,
            street2: this.newAddressInputEls.street2.el.value,
            city: this.newAddressInputEls.city.el.value,
            zip: this.newAddressInputEls.zip.el.value,
            state_id: this.newAddressInputEls.province.el?.value,
            country_id: this.newAddressInputEls.country.el.value,
        };
    }

    async saveDeliveryAddress(deliveryAddressId) {
        let sale_order_line_id = this.solId;
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
                alert(e.message?.data?.message || e.toString());
            });
        });
    }

    async onChangedDeliveryAddressData() {
        let sale_order_line_id = this.solId;
        let deliveryAddressData  = await rpc.query({
                route: '/shop/cart/get_delivery_addresses_data',
                params: {
                    sale_order_line_id,
                },
            }).catch((e) => {
                alert(e.message?.data?.message || e.toString());
            });
        // updates props
        this.props.solData = JSON.parse(deliveryAddressData);
        this.render();
        this.hideInputFormModal();
    }

    onChangedCountrySelection(ev) {
        this.state.currentCountryHasProvinces = ev.target.selectedOptions[0].dataset.hasOwnProperty('hasProvince')
        this.state.currentCountryId = ev.target.value;
    }
}

DeliveryAddressCartLine.props = {
    solData: {
        type: Object,
    },
}
DeliveryAddressCartLine.template = 'address_cart_line';

mountComponentAsWidget('DeliveryAddressCartLine', DeliveryAddressCartLine).catch();
