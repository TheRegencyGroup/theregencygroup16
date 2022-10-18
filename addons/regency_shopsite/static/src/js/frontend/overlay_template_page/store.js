/** @odoo-module **/

import { env, addStore } from '../base/main';
import Dialog from 'web.Dialog';

const OVERLAY_TEMPLATE_PAGE_KEY = 'overlay_template_page_key';
const CHANGE_ATTRIBUTE_VALUE_ACTION = 'change_attribute_value_action';

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
    const actions = {
        [CHANGE_ATTRIBUTE_VALUE_ACTION] ({state}, attributeId, valueId) {
            state[OVERLAY_TEMPLATE_PAGE_KEY].selectedAttributeValues[attributeId].valueId = valueId;
        },
    };
    const state = {
        [OVERLAY_TEMPLATE_PAGE_KEY]: {
            data: overlayTemplatePageData,
            selectedAttributeValues: getSelectedAttributeValues(),
        },
    };
    addStore(actions, state);
}

export {
    OVERLAY_TEMPLATE_PAGE_KEY,
    CHANGE_ATTRIBUTE_VALUE_ACTION,
}

