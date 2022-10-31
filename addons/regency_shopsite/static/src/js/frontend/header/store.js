/** @odoo-module **/

import { extendStore } from '@fe_owl_base/js/main';
import Concurrency from 'web.concurrency';
import env from 'web.public_env';

const hotelSelectorData = PRELOADED_DATA?.HEADER_DATA;

if (hotelSelectorData) {
    const dropPrevious = new Concurrency.MutexedDropPrevious();

    class HotelSelector {
        constructor() {
            for (let [key, value] of Object.entries(hotelSelectorData)) {
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
            if (this.isNoActiveHotel) {
                return "";
            }
            return this.hotels[this.activeHotel].name;
        }

        get currentHotelLogoUrl() {
            if (this.isNoActiveHotel) {
                return "";
            }
            return this.hotels[this.activeHotel].logo_url;
        }

        get currentHotelBackgroundUrl() {
            if (this.isNoActiveHotel) {
                return "";
            }
            return this.hotels[this.activeHotel].background_url;
        }

        get isNoActiveHotel() {
            return !this.activeHotel || !this.hotels[this.activeHotel]
        }

        _updateActiveHotel = () => {
            return env.services.rpc({
                route: "/user/active_hotel",
                method: "POST",
                params: {
                    hotel: this.activeHotel,
                },
            }).then(() => {
                env.bus.trigger('active-hotel-changed');
            });
        }

        setActiveHotel(value) {
            value = parseInt(value);
            this._activeHotel = value;
            dropPrevious.exec(this._updateActiveHotel);
            this._setActiveHotelBackground()
        }

        _setActiveHotelBackground() {
            let backgroundUrl = this.currentHotelBackgroundUrl
            let cssRec = 'background: ""'
            if (backgroundUrl && !this.isNoActiveHotel) {
                cssRec = `background: url(${backgroundUrl}) center center no-repeat;`
            }
            document.querySelector('.regency-top').style = cssRec
        }
    }

    extendStore({ key: 'hotelSelector', obj: new HotelSelector() });
}
