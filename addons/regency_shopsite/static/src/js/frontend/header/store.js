/** @odoo-module **/

import { extendStore } from '@fe_owl_base/js/main';

const headerData = PRELOADED_DATA?.HEADER_DATA;

if (headerData) {
    class Store {
        constructor() {
            for (let [key, value] of Object.entries(headerData)) {
                this[key] = value;
            }
            this.hotel_ids = this.hotel_ids.reduce((acc, x) => {
                acc[x.id] = x;
                return acc;
            }, {});
        }

        get currentHotelName() {
            if (!this.active_hotel_id || !this.hotel_ids[this.active_hotel_id]) {
                return "";
            }
            return this.hotel_ids[this.active_hotel_id].name;
        }
    }

    extendStore({ header: new Store() });
}
