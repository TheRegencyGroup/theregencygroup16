/** @odoo-module **/

const { Component, useRef, useState, useEnv } = owl;

export const TEXT_AREA_ALIGN_LIST = ['left', 'center', 'right'];

class AreaParametersNumberInput extends Component {
    setup() {
        this.input = useRef('input')
    }

    get value() {
        return parseInt(this.input.el.value);
    }

    changeValue() {
        this.props.changeValue(this.props.areaIndex, this.value);
    }

    onChangeInput() {
        this.changeValue();
        this.prevInputValue = this.value;
    }

    onInput() {
        if (!this.prevInputValue) {
            this.prevInputValue = this.props.value;
        }
        if (!this.input.el.validity.valid) {
            this.input.el.value = this.prevInputValue;
        } else {
            this.prevInputValue = this.input.el.value;
        }
    }
}

AreaParametersNumberInput.defaultProps = {
    inputStep: 1,
};

AreaParametersNumberInput.props = {
    areaIndex: Number,
    label: String,
    value: Number,
    disabled: Boolean,
    inputMin: {
        type: Number,
        optional: true,
    },
    inputMax: {
        type: Number,
        optional: true,
    },
    changeValue: Function,
};

AreaParametersNumberInput.template = 'areas_parameters_number_input';

export class AreaParameters extends Component {
    setup() {
        this.TEXT_AREA_ALIGN_LIST = TEXT_AREA_ALIGN_LIST;

        this.env = useEnv();
    }

    onChangeFont(event) {
        const option =  event.target.selectedOptions[0];
        let fontId = option.value;
        if (!fontId.startsWith('default_')) {
            fontId = parseInt(fontId);
        }
        this.props.area.change.font(this.props.area.index, {
            id: fontId,
            name: option.dataset.name,
        });
    }

    onChangeTextColor(event) {
        const option =  event.target.selectedOptions[0];
        let colorId = parseInt(option.value);
        this.props.area.change.color(this.props.area.index, {
            id: colorId,
            name: option.dataset.name,
            color: option.dataset.color,
        });
    }

    onChangeTextAlign(event) {
        const option =  event.target.selectedOptions[0];
        this.props.area.change.align(this.props.area.index, option.value);
    }

    onClickAreaListItem() {
        this.props.selectArea(this.props.area.index);
    }

    onClickRemoveArea() {
        this.props.removeArea(this.props.area.index);
    }
}

AreaParameters.components = {
    AreaParametersNumberInput,
};

AreaParameters.props = {
    area: Object,
    editMode: Boolean,
    selectedAreaIndex: Number,
    selectArea: Function,
    removeArea: Function,
    fontList: Array,
    colorList: Array,
};

AreaParameters.template = 'areas_parameters';
