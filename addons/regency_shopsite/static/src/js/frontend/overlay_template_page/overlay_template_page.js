/** @odoo-module **/

import {mountComponentAsWidget, useStore} from '@fe_owl_base/js/main';
import {OVERLAY_TEMPLATE_PAGE_KEY} from './store';
import {ProductOverlayEditorComponent} from './product_overlay_editor';

const {Component, useState} = owl;

export class OverlayTemplatePageComponent extends Component {
    setup() {
        this.store = useStore()[OVERLAY_TEMPLATE_PAGE_KEY];
        this.state = useState({});
    }
}

OverlayTemplatePageComponent.components = {
    ProductOverlayEditorComponent,
};

OverlayTemplatePageComponent.template = 'overlay_template_page';

mountComponentAsWidget('OverlayTemplatePageComponent', OverlayTemplatePageComponent).catch();
