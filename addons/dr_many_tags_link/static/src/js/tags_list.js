/** @odoo-module **/

import { TagsList } from '@web/views/fields/many2many_tags/tags_list';
import { patch } from 'web.utils';
import { useService } from '@web/core/utils/hooks';

patch(TagsList.prototype, 'dr_many_tags_link/static/src/js/tags_list', {
    setup() {
        this._super(...arguments)
        this.action = useService('action')
    },

    onClickAction(ev, tag) {
        if (ev.shiftKey) {
            return tag.onClick && tag.onClick(ev)
        } else {
            return this.getActionForm(tag.resId, tag.resModel, tag.text);
        }
    },

    getActionForm(resId, resModel, title) {
        return this.action.doAction({
            res_model: resModel,
            res_id: resId,
            name: title,
            type: "ir.actions.act_window",
            views: [[false, "form"]],
            view_mode: "form",
            target: "current",
        });
    },
});