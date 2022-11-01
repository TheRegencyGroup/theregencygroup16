/** @odoo-module **/

require( '@dr_many_tags_link/js/tags_list');
import { TagsList } from '@web/views/fields/many2many_tags/tags_list';
import { patch } from 'web.utils';


patch(TagsList.prototype, 'regency_estimate/static/src/js/tags_list', {

    onClickAction(ev, tag) {
       if (!ev.shiftKey && tag.resModel === 'product.price.sheet.line') {
            let text = tag.text;
            fetch('/price_sheet/get/' + tag.resId).then((response) => response.json())
                .then((data) => { return this.getActionForm(data.ps_id, 'product.price.sheet', text)});
        } else {
            return this._super(ev, tag);
        }
    },

});