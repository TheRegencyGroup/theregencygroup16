/** @odoo-module */

import publicWidget from 'web.public.widget';

publicWidget.registry.PortalSaleLegalAccepted = publicWidget.Widget.extend({
    selector: '.regency_legal_accept',
    events: {
        'change #legal_accept': '_onChangeLegalAccepted',
    },

    _onChangeLegalAccepted(event) {
        let saleOrderId = parseInt(event.target.dataset.saleOrderId);
        let checked = event.target.checked;
        if (!saleOrderId) {
            event.target.checked = !checked;
            return;
        }
        this._rpc({
            model: 'sale.order',
            method: 'toggle_legal_accepted',
            args: [saleOrderId],
            kwargs: {
                checked,
            },
        }).then((data) => {
            event.target.checked = data;
            for (let btn of document.querySelectorAll('a[data-sale-order-confirm-btn="1"]')) {
                btn.dataset.saleOrderLegalAccepted = data ? 'True' : 'False';
            }
        }).guardedCatch((error) => {
            event.target.checked = !checked;
        });
    },

});
