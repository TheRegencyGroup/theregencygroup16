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
            this.quantity = this.selectedPriceId ? this.selectedPrice.quantity : null;
            this.editMode = false;

            this._checkOverlayProductIdUrlParameter();

            this.attrributesWasChanged = false;
        }

        get overlayPositions() {
            return this.overlayTemplate?.positionsData || {};
        }

        get selectedAreasImageAttributeValueId() {
            if (this.areasImageAttributeId) {
                return this.selectedAttributeValues[this.areasImageAttributeId].valueId;
            }
            return false;
        }

        get hasOverlayProductId() {
            return !!this.overlayProduct?.id;
        }

        get hasPriceList() {
            return this.priceList && Object.values(this.priceList).length;
        }

        get canAddedToCart() {
            return this.overlayTemplate?.isAvailableForActiveHotel &&
                this.hasPriceList && !this.overlayProductIsArchived;
        }

        get overlayProductIsArchived() {
            return this.hasOverlayProductId && !this.overlayProduct?.active;
        }

        get sortedPriceList() {
            if (this.priceList && Object.values(this.priceList).length) {
                return Object.values(this.priceList).sort((a, b) => a.quantity - b.quantity);
            }
            return [];
        }

        get selectedPrice() {
            return this.priceList[this.selectedPriceId];
        }

        get minimumOrderQuantity() {
            if (this.priceList && Object.values(this.priceList).length) {
                return Math.min(...Object.values(this.priceList).map(e => e.quantity));
            }
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
            return this.sortedPriceList.length ? this.sortedPriceList[0].id : null;
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
            let url = new URL(window.location.href);
            let paramKey = this.options?.overlayProductIdUrlParameter;
            if (this.hasOverlayProductId) {
                url.searchParams.set(paramKey, this.overlayProduct.id);
            } else {
                url.searchParams.delete(paramKey);
            }
            window.history.replaceState(null, null, url);
        }

        changeAttributeValueAction(attributeId, valueId) {
            if (this.selectedAttributeValues[attributeId].valueId !== valueId) {
                this.selectedAttributeValues[attributeId].valueId = valueId;
                this.attrributesWasChanged = true;
            }
        }

        changeSelectedPrice(priceId) {
            this.selectedPriceId = priceId;
            this.quantity = this.selectedPrice.quantity;
        }

        changeQuantity(qty) {
            this.quantity = qty;
            let prices = this.sortedPriceList;
            if (prices.length === 1) {
                return;
            }
            let changed = false;
            for (let [index, e] of prices.entries()) {
                const min = index === 0 ? 0 : prices[index - 1].quantity;
                const max = e.quantity;
                if (this.quantity >= min && this.quantity < max) {
                    this.selectedPriceId = index === 0 ? e.id : prices[index - 1].id;
                    changed = true;
                    break;
                }
            }
            if (!changed) {
                this.selectedPriceId = prices.pop().id;
            }
        }

        getCustomizedData() {
            return {
                overlayTemplateId: this.overlayTemplate?.id,
                attributeList: Object.entries(this.selectedAttributeValues)
                    .map(e => ({ 'attribute_id': parseInt(e[0]), value_id: e[1].valueId })),
                quantity: this.quantity,
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
                    overlay_product_id: this.overlayProduct?.id,
                    overlay_product_was_changed: overlayProductWasChanged || false,
                };
            }
            if (this.duplicateOverlayProductId) {
                params.duplicate_overlay_product_id = this.duplicateOverlayProductId;
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
                        overlay_product_id: this.overlayProduct?.id,
                    },
                });
                if (res) {
                    window.location.replace('/shop?tab=op');
                }
            } catch (e) {
                alert(e.message?.data?.message || e.toString())
            }
        }

        duplicateOverlayProduct() {
            this.duplicateOverlayProductId = this.overlayProduct.id;
            this.overlayProduct.id = null;
            this.overlayProduct.name = this.overlayProduct.name + ' (Copy)';
            this.overlayProduct.active = null;
            this._updateOverlayProductIdUrlParameter();
        }

        async updatePriceList(activeHotelId) {
            if (activeHotelId) {
                this.overlayTemplateIsAvailableForActiveHotel = this.overlayTemplate?.hotelIds.includes(activeHotelId);
            }
            try {
                let res = await rpc.query({
                    route: '/shop/overlay_template/price_list',
                    params: {
                        overlay_template_id: this.overlayTemplate?.id,
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
            this.duplicateOverlayProductId = null;
            if (!this.overlayProduct) {
                this.overlayProduct = {};
            }
            Object.assign(this.overlayProduct, data);
            this._updateOverlayProductIdUrlParameter();
        }
    }

    extendStore({ key: 'otPage', obj: new OverlayTemplatePage() })
}
