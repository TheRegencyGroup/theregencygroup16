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
            this.editMode = false;

            this._checkOverlayProductIdUrlParameter();

            this.attrributesWasChanged = false;
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

        get hasPriceList() {
            return this.priceList && Object.values(this.priceList).length;
        }

        get canAddedToCart() {
            return this.overlayTemplateIsAvailableForActiveHotel &&
                this.hasPriceList &&
                ((this.hasOverlayProductId && this.overlayProductActive) || !this.hasOverlayProductId);
        }

        get overlayProductIsArchived() {
            return this.hasOverlayProductId && !this.overlayProductActive;
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

        _checkOverlayProductIdUrlParameter() {
            if (!this.hasOverlayProductId) {
                let url = new URL(window.location.href);
                let paramKey = this.options?.overlayProductIdUrlParameter;
                if (url.searchParams.get(paramKey)) {
                    url.searchParams.delete(paramKey);
                    window.history.replaceState(null, null, url);
                }
            }
        }

        _updateOverlayProductIdUrlParameter() {
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
                this.attrributesWasChanged = true;
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
                quantity: this.hasPriceList ? this.priceList[this.selectedPriceId].quantity : null,
            };
        }

        enableEditMode() {
            this.editMode = true;
            this.attrributesWasChanged = false;
        }

        disableEditMode() {
            this.editMode = false;
            this.attrributesWasChanged = false;
        }

        async saveOverlayProduct({ overlayProductName, overlayAreaList, previewImagesData, overlayProductWasChanged }) {
            let data = this.getCustomizedData();
            let params = {
                overlay_template_id: data.overlayTemplateId,
                overlay_product_name: overlayProductName,
            };
            if (!this.hasOverlayProductId || (this.hasOverlayProductId && overlayProductWasChanged)) {
                params = {
                    ...params,
                    attribute_list: data.attributeList,
                    overlay_area_list: overlayAreaList,
                    preview_images_data: previewImagesData,
                };
            }
            if (this.hasOverlayProductId && this.editMode) {
                params = {
                    ...params,
                    overlay_product_id: this.overlayProductId,
                    overlay_product_was_changed: overlayProductWasChanged || false,
                };
            }
            try {
                let res = await rpc.query({
                    route: '/shop/overlay_template/save',
                    params,
                });
                if (res) {
                    this.updateOverlayProductData(res);
                }
            } catch (e) {
                alert(e.message?.data?.message || e.toString())
            }
        }

        async deleteOverlayProduct() {
            if (!this.hasOverlayProductId) {
                return;
            }
            try {
                let res = await rpc.query({
                    route: '/shop/overlay_template/delete',
                    params: {
                        overlay_product_id: this.overlayProductId,
                    },
                });
                if (res) {
                    window.location.replace('/shop?tab=op');
                }
            } catch (e) {
                alert(e.message?.data?.message || e.toString())
            }
        }

        async updatePriceList(activeHotelId) {
            if (activeHotelId) {
                this.overlayTemplateIsAvailableForActiveHotel = this.overlayTemplateHotelIds.includes(activeHotelId);
            }
            try {
                let res = await rpc.query({
                    route: '/shop/overlay_template/price_list',
                    params: {
                        overlay_template_id: this.overlayTemplateId,
                    },
                });
                if (res) {
                    Object.assign(this, res);
                    this.selectedPriceId = this.getSelectedPriceId();
                }
            } catch (e) {
                alert(e.message?.data?.message || e.toString())
            }
        }

        updateOverlayProductData(data) {
            Object.assign(this, data);
            this._updateOverlayProductIdUrlParameter();
        }
    }

    extendStore({ key: 'otPage', obj: new OverlayTemplatePage() })
}
