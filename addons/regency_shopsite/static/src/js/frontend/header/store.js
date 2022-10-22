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
                let _key = '_' + key;
                this[_key] = value;
                Object.defineProperty(this, key, {
                    get() {
                        return this[_key];
                    },
                    set() {
                        throw new Error("Use action to change store values");
                    }
                });
            }
            this._hotels = this._hotels.reduce((acc, x) => {
                acc[x.id] = x;
                return acc;
            }, {});
        }

        get currentHotelName() {
            if (!this.activeHotel || !this.hotels[this.activeHotel]) {
                return "";
            }
            return this.hotels[this.activeHotel].name;
        }

        _updateActiveHotel = () => {
            return env.services.rpc({
                route: "/user/active_hotel",
                method: "POST",
                params: {
                    hotel: this.activeHotel,
                },
            });
        }

        setActiveHotel(value) {
            value = parseInt(value);
            this._activeHotel = value;
            dropPrevious.exec(this._updateActiveHotel);
        }
    }

    extendStore({ key: 'header', obj: new Store() });
}
