/** @odoo-module **/

import './store';
import { useStore } from '@fe_owl_base/js/main';

const { Component } = owl;

export class AttributeSelector extends Component {
    setup() {
        this.store = useStore();
    }

    get attribute() {
        return this.store.otPage.attributeList[this.props.attributeId];
    };

    onChangeAttributeValue(valueId) {
        this.store.otPage.changeAttributeValueAction(this.props.attributeId, valueId);
    }
}

AttributeSelector.props = {
    attributeId: Number,
}

AttributeSelector.template = 'overlay_template_page_attribute_selector';

export class ColorAttributeSelector extends AttributeSelector {}

ColorAttributeSelector.template = 'overlay_template_page_color_attribute_selector';
