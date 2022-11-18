/** @odoo-module **/

import { FormStatusIndicator } from '@web/views/form/form_status_indicator/form_status_indicator';
import { patch } from 'web.utils';

patch(FormStatusIndicator.prototype, 'regency_shopsite', {
    async discard() {
        this.env.bus.trigger('discard-changes', {});
        await this._super(...arguments);
    },
});
