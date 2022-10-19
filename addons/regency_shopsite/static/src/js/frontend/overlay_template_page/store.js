/** @odoo-module **/

import { Store } from '@fe_owl_base/js/main';
import { patch } from "web.utils";

const OVERLAY_TEMPLATE_PAGE_KEY = 'overlay_template_page_key';

const overlayTemplatePageData = PRELOADED_DATA?.OVERLAY_TEMPLATE_PAGE_DATA;
if (overlayTemplatePageData) {
    function getSelectedAttributeValues() {
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

    patch(Store.prototype, 'overlay_product_page', {
        [OVERLAY_TEMPLATE_PAGE_KEY]: {
            ...overlayTemplatePageData,
            selectedAttributeValues: getSelectedAttributeValues(),
        },
        get overlayPositions() {
            return this[OVERLAY_TEMPLATE_PAGE_KEY].overlayTemplateAreasData?.overlayPositions || {};
        },
        get colorValueId() {
            const selectedAttributeValues = this[OVERLAY_TEMPLATE_PAGE_KEY].selectedAttributeValues;
            const colorAttributeId = this[OVERLAY_TEMPLATE_PAGE_KEY].colorAttributeId;
            return {
                colorValueId: selectedAttributeValues[colorAttributeId].valueId,
            }
        },
        changeAttributeValueAction (attributeId, valueId) {
            this[OVERLAY_TEMPLATE_PAGE_KEY].selectedAttributeValues[attributeId].valueId = valueId;
        },
    });
}

export {
    OVERLAY_TEMPLATE_PAGE_KEY,
}
