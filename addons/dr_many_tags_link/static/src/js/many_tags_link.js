/** @odoo-module **/

import {
    Many2ManyTagsField,
    Many2ManyTagsFieldColorEditable
} from '@web/views/fields/many2many_tags/many2many_tags_field';
import { patch } from 'web.utils';
import { registry } from "@web/core/registry";

patch(Many2ManyTagsField.prototype, 'dr_many_tags_link/static/src/js/many_tags_link', {
    getTagProps(record) {
        let props = this._super(...arguments);
        Object.assign(props, {
            resModel: record.resModel,
        });
        return props;
    },
});

registry.category("fields").add("list.many2many_tags", Many2ManyTagsFieldColorEditable);
