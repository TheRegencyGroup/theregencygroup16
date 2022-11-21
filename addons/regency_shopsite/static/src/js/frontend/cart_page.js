/** @odoo-module **/

import publicWidget from 'web.public.widget';
import Dialog from 'web.Dialog';

publicWidget.registry.SubmitCart = publicWidget.Widget.extend({
    selector: '.oe_website_sale',
    events: {
        'click button.submit_cart': '_onClickSubmit',
    },

    async _onClickSubmit(event) {
        new Promise((resolve, reject) => {
            Dialog.confirm(
                this,
                'Are you sure that you want to submit the cart? Once you submit, the cart will become unavailable for editing',
                {
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
