/** @odoo-module **/

import { TagsList } from '@web/views/fields/many2many_tags/tags_list';
import { patch } from 'web.utils';

patch(TagsList.prototype, 'dr_many_tags_link/static/src/js/tags_list', {
    onClickAction(resId, resModel, title) {
        return this.getActionForm(resId, resModel, title);
    },

    getActionForm(resId, resModel, title) {
        return this.env.services.action.doAction({
            res_model: resModel,
            res_id: resId,
            name: title,
            type: "ir.actions.act_window",
            views: [[false, "form"]],
            view_mode: "form",
            target: "new",
        });
    },
});