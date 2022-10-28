/** @odoo-module **/

import './store';
import { useStore } from '@fe_owl_base/js/main';

const { Component } = owl;

class AttributeSelectorValue extends Component {
    setup() {
        this.store = useStore();
    }

    get isChecked() {
        return this.store.otPage.selectedAttributeValues[this.props.attribute.id].valueId === this.props.value.id;
    }

    get showValue() {
        return this.isChecked || (!this.isChecked && (!this.store.otPage.hasOverlayProductId || this.store.otPage.editMode));
    }

    onChangeAttributeValue() {
        this.store.otPage.changeAttributeValueAction(this.props.attribute.id, this.props.value.id);
    }
}

AttributeSelectorValue.props = {
    attribute: Object,
    value: Object,
};

AttributeSelectorValue.template = 'overlay_template_page_attribute_selector_value';

export class AttributeSelector extends Component {
    setup() {
        this.store = useStore();
    }

    get attribute() {
        return this.store.otPage.attributeList[this.props.attributeId];
    }
}

AttributeSelector.components = {
    AttributeSelectorValue,
};

AttributeSelector.props = {
    attributeId: Number,
};

AttributeSelector.template = 'overlay_template_page_attribute_selector';

class ColorAttributeSelectorValue extends AttributeSelectorValue {}

ColorAttributeSelectorValue.template = 'overlay_template_page_color_attribute_selector_value';

export class ColorAttributeSelector extends AttributeSelector {}

ColorAttributeSelector.components = {
    ColorAttributeSelectorValue,
};

ColorAttributeSelector.template = 'overlay_template_page_color_attribute_selector';
