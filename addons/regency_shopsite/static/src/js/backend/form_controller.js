/** @odoo-module **/

import FormController from 'web.FormController';
import env from 'web.env';

FormController.include({
    saveRecord: async function () {
        return this._super(...arguments);
    },
});
