/** @odoo-module */

import { registry } from "@web/core/registry";
import { X2ManyField } from "@web/views/fields/x2many/x2many_field";


export class X2ManyNoSelection extends X2ManyField {
    setup() {
        super.setup();
        this.selectCreate = (params) => {
            let context = params.context;
            this._openRecord({ context })
        };
    }
}

registry.category("fields").add("x2many_no_selection", X2ManyNoSelection);
