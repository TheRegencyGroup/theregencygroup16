/** @odoo-module **/

import { Many2ManyTagsField } from '@web/views/fields/many2many_tags/many2many_tags_field';
import { patch } from 'web.utils';

patch(Many2ManyTagsField.prototype, 'dr_many_tags_link/static/src/js/many_tags_link', {
    getTagProps(record) {
        let props = this._super(...arguments);
        Object.assign(props, {
            resModel: record.resModel,
        });
        console.log(props);
        return props;
    },
});
