/** @odoo-module **/
import { env } from '@fe_owl_base/js/main';
import PublicWidget from 'web.public.widget';


PublicWidget.registry.ReorderCart = PublicWidget.Widget.extend({
    selector: '.card-body',
    events: {
        'click #reorder': '_onClickReorder',
        'click .reorder_line': '_onClickReorderLine',
    },

    async _onClickReorderLine(ev) {
        if (this.blockReordering) {
            return
        }
        this.blockReordering = true;
        try {
            let res = await this._rpc({
                route: "/shop/cart/reorder",
                params: {
                    sale_order_line_id: parseInt(ev.target.dataset.lineId)
                },
            });
            env.store.cart.updateData(res);
        } catch (e) {
            alert(e);
        }
        this.blockReordering = false;
    },
});
