/** @odoo-module **/

import { env, mountComponentAsWidget } from '../base/main';
import {
    OVERLAY_TEMPLATE_PAGE_KEY,
    CHANGE_ATTRIBUTE_VALUE_ACTION,
} from './store';
import { ProductOverlayEditorComponent } from './product_overlay_editor';

const { Component } = owl;
const { useStore, useState, useDispatch } = owl.hooks;

export class OverlayTemplatePageComponent extends Component {
    constructor (...args) {
        super(...args);

        this.dispatch = useDispatch();

        this.store = useStore(state => ({
            data: state[OVERLAY_TEMPLATE_PAGE_KEY].data,
            selectedAttributeValues: state[OVERLAY_TEMPLATE_PAGE_KEY].selectedAttributeValues,
        }), {
            store: env.store,
        });

        this.state = useState({

        });
    }

    onChangeAttributeValue(attributeId, valueId, event) {
        this.dispatch(CHANGE_ATTRIBUTE_VALUE_ACTION, attributeId, valueId);
    }
}

OverlayTemplatePageComponent.components = {
    ProductOverlayEditorComponent,
};

OverlayTemplatePageComponent.template = 'overlay_template_page';

mountComponentAsWidget('OverlayTemplatePageComponent', OverlayTemplatePageComponent).catch();
