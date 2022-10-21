/** @odoo-module **/

import { extendStore } from '@fe_owl_base/js/main';

const overlayTemplatePageData = PRELOADED_DATA?.OVERLAY_TEMPLATE_PAGE_DATA;
if (overlayTemplatePageData) {
    class OverlayTemplatePage {
        constructor() {
            for (let [key, value] of Object.entries(overlayTemplatePageData)) {
                this[key] = value;
            }
            this.selectedAttributeValues = this.getSelectedAttributeValues();
            this.selectedPriceId = this.priceList ? Object.values(this.priceList)[0].id : null;
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

        get overlayPositions() {
            return this.overlayTemplateAreasData?.overlayPositions || {};
        }

        get selectedColorValueId() {
            const selectedAttributeValues = this.selectedAttributeValues;
            const colorAttributeId = this.colorAttributeId;
            return selectedAttributeValues[colorAttributeId].valueId;
        }

        changeAttributeValueAction(attributeId, valueId) {
            this.selectedAttributeValues[attributeId].valueId = valueId;
        }

        changeSelectedPrice(priceId) {
            this.selectedPriceId = priceId;
        }
    }

    extendStore({ otPage: new OverlayTemplatePage() })
}
