/** @odoo-module **/

import { registry } from "@web/core/registry";
import rpc from 'web.rpc';

import { usePopover } from "@web/core/popover/popover_hook";

const { Component, EventBus, onWillRender } = owl;

export class MultiCurrencyPopOver extends Component {
}

MultiCurrencyPopOver.template = "multi_currency_widget.MultiCurrencyPopOver";

export class MultiCurrencyWidget extends Component {
    setup() {
        this.bus = new EventBus();
        this.popover = usePopover();
        this.closePopover = null;
        this.calcData = [];
        onWillRender(() => {
            this.initCalcData();
        })
    }

    initCalcData() {
        this.updateCalcData();
    }

    updateCalcData() {
        // popup specific data
        let self = this;
        let value_field = this.props.options['value_field'];
        let currency_field = this.props.options['currency_field'];
        let date_field = this.props.options['date_field'];

        rpc.query({
                    model: this.props.record.resModel,
                    method: 'get_currencies_values',
                    args: [[this.props.record.data['id']], value_field, currency_field, date_field],
                }).then(result => {
                    self.calcData = result;
                })
    }

    showPopup(ev) {
        this.updateCalcData();
        this.closePopover = this.popover.add(
            ev.currentTarget,
            this.constructor.components.Popover,
            {bus: this.bus, record: this.props.record, calcData: this.calcData},
            {
                position: 'top',
            }
            );
        this.bus.addEventListener('close-popover', this.closePopover);
    }
}

MultiCurrencyWidget.components = { Popover: MultiCurrencyPopOver };
MultiCurrencyWidget.template = "multi_currency_widget.MultiCurrencyWidget";

registry.category("view_widgets").add("multi_currency_widget", MultiCurrencyWidget);
