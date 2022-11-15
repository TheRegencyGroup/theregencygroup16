/** @odoo-module **/

import publicWidget from 'web.public.widget';
import Dialog from 'web.Dialog';

publicWidget.registry.SubmitCart = publicWidget.Widget.extend({
    selector: '.submit_cart',
    events: {
        'click': '_onClickSubmit',
    },

    async _onClickSubmit(event) {
        new Promise((resolve, reject) => {
            Dialog.confirm(this, 'You want to submit the order?', {
                confirm_callback: resolve,
                cancel_callback: reject,
            }).on('closed', null, reject);
        }).then(confirm => {
            if (!confirm) {
                return;
            }
            this._rpc({
                route: '/shop/submit_cart',
                params: {},
            }).then(submit => {
                if (submit) {
                    window.location = '/shop';
                }
            }).catch(e => {
                alert(e.message?.data?.message || e.toString())
            });
        });
    },
});