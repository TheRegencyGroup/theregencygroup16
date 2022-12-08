/** @odoo-module **/

import { Record } from '@web/views/basic_relational_model';
import legacyEnv from "web.env";
import { patch } from 'web.utils';

patch(Record.prototype, 'regency_shopsite/static/src/js/backend/basic_relation_model', {
    async update(changes) {
        await this._super(changes)
        legacyEnv.bus.trigger('change-field', { changes });
    },
});
