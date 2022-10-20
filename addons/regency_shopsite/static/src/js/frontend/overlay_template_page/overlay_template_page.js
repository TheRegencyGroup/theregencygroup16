/** @odoo-module **/

import { mountComponentAsWidget, useStore } from '@fe_owl_base/js/main';
import { ProductOverlayEditorComponent } from './product_overlay_editor';

const { Component, useState } = owl;

export class OverlayTemplatePageComponent extends Component {
    setup() {
        this.store = useStore();
        this.state = useState({});
    }

    onChangeAttributeValue(attributeId, valueId) {
        this.store.otPage.changeAttributeValueAction(attributeId, valueId);
    }
}

OverlayTemplatePageComponent.components = {
    ProductOverlayEditorComponent,
};

OverlayTemplatePageComponent.template = 'overlay_template_page';

mountComponentAsWidget('OverlayTemplatePageComponent', OverlayTemplatePageComponent).catch();
