/** @odoo-module **/

import { extendStore } from '@fe_owl_base/js/main';
import Concurrency from 'web.concurrency';
import env from 'web.public_env';

const headerData = PRELOADED_DATA?.HEADER_DATA;

if (headerData) {
    const dropPrevious = new Concurrency.MutexedDropPrevious();

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

        _updateActiveHotel = () => {
            return env.services.rpc({
                route: "/user/active_hotel",
                method: "POST",
                params: {
                    hotel: this.active_hotel_id,
                },
            });
        }

        setActiveHotel(value) {
            value = parseInt(value);
            this.active_hotel_id = value;
            dropPrevious.exec(this._updateActiveHotel);
        }
    }

    extendStore({ key: 'header', obj: new Store() });
}
