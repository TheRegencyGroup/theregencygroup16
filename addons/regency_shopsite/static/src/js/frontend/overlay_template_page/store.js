/** @odoo-module **/

import { extendStore } from '@fe_owl_base/js/main';
import rpc from 'web.rpc';

const overlayTemplatePageData = PRELOADED_DATA?.OVERLAY_TEMPLATE_PAGE_DATA;
if (overlayTemplatePageData) {
    class OverlayTemplatePage {
        constructor() {
            for (let [key, value] of Object.entries(overlayTemplatePageData)) {
                this[key] = value;
            }
            this.selectedAttributeValues = this.getSelectedAttributeValues();
            this.selectedPriceId = this.getSelectedPriceId();

            this.#checkOverlayProductIdUrlParameter();
        }

        get overlayPositions() {
            return this.overlayTemplateAreasData?.overlayPositions || {};
        }

        get selectedColorValueId() {
            const selectedAttributeValues = this.selectedAttributeValues;
            const colorAttributeId = this.colorAttributeId;
            return selectedAttributeValues[colorAttributeId].valueId;
        }

        get hasOverlayProductId() {
            return !!this.overlayProductId;
        }

        getSelectedAttributeValues() {
            let res = {};
            const attributeList = Object.values(overlayTemplatePageData.attributeList);
            if (attributeList) {
                res = attributeList.reduce((a, e) => ({
                    ...a,
                    [e.id]: {
                        'attributeName': e.name,
                        'valueId': e.selectedValueId,
                    }
                }), {});
            }
            return res;
        }

        getSelectedPriceId() {
            const priceList = Object.values(this.priceList);
            return priceList.length ? priceList[0].id : null;
        }

        #checkOverlayProductIdUrlParameter() {
            if (!this.hasOverlayProductId) {
                let url = new URL(window.location.href);
                let paramKey = this.options?.overlayProductIdUrlParameter;
                if (url.searchParams.get(paramKey)) {
                    url.searchParams.delete(paramKey);
                    window.history.replaceState(null, null, url);
                }
            }
        }

        updateOverlayProductIdUrlParameter() {
            if (this.hasOverlayProductId) {
                let url = new URL(window.location.href);
                let paramKey = this.options?.overlayProductIdUrlParameter;
                url.searchParams.set(paramKey, this.overlayProductId);
                window.history.replaceState(null, null, url);
            }
        }

        changeAttributeValueAction(attributeId, valueId) {
            if (this.selectedAttributeValues[attributeId].valueId !== valueId) {
                this.selectedAttributeValues[attributeId].valueId = valueId;
            }
        }

        changeSelectedPrice(priceId) {
            this.selectedPriceId = priceId;
        }

        getCustomizedData() {
            return {
                overlayTemplateId: this.overlayTemplateId,
                attributeList: Object.entries(this.selectedAttributeValues)
                    .map(e => ({ 'attribute_id': parseInt(e[0]), value_id: e[1].valueId })),
                quantity: this.priceList[this.selectedPriceId].quantity,
            };
        }

        async saveOverlayProduct({ overlayProductName, overlayAreaList }) {
            let data = this.getCustomizedData();
            try {
                let res = await rpc.query({
                    route: '/shopsite/overlay_template/save',
                    params: {
                        overlay_template_id: data.overlayTemplateId,
                        attribute_list: data.attributeList,
                        overlay_product_name: overlayProductName,
                        overlay_area_list: overlayAreaList,
                    },
                });
                if (res) {
                    Object.assign(this, res);
                    this.updateOverlayProductIdUrlParameter();
                }
            } catch (e) {
                console.log(e)
            }
        }

        async updatePriceList(activeHotelId) {
            if (activeHotelId) {
                this.overlayTemplateIsAvailableForActiveHotel = this.overlayTemplateHotelIds.includes(activeHotelId);
            }
            try {
                let res = await rpc.query({
                    route: '/shopsite/overlay_template/price_list',
                    params: {
                        overlay_template_id: this.overlayTemplateId,
                    },
                });
                if (res) {
                    Object.assign(this, res);
                    this.selectedPriceId = this.getSelectedPriceId();
                }
            } catch (e) {
                console.log(e)
            }
        }

        async updateOverlayProductData(data) {
            Object.assign(this, data);
            this.updateOverlayProductIdUrlParameter();
        }
    }

    extendStore({ key: 'otPage', obj: new OverlayTemplatePage() })
}
