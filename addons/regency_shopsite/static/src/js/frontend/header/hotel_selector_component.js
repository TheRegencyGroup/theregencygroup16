/** @odoo-module **/

import './store';
import { mountComponentAsWidget, useStore } from '@fe_owl_base/js/main';
const { Component, useState } = owl;

export class HotelSelectorComponent extends Component {
    setup() {
        this.store = useStore();
        this.state = useState({ isOpen: false });
    }

    onToggle() {
        this.state.isOpen = !this.state.isOpen;
    }

    onSelect(e) {
        this.store.hotelSelector.setActiveHotel(e.currentTarget.dataset.id);
        this.state.isOpen = false;
    }
}

HotelSelectorComponent.components = {};

HotelSelectorComponent.template = 'hotel_selector_component';

mountComponentAsWidget('HotelSelectorComponent', HotelSelectorComponent).catch();
