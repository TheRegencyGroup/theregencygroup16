/** @odoo-module */

import publicWidget from 'web.public.widget';

const HIGHLIGHT_CLASS = 'highlight';

publicWidget.registry.SalePortalConfirm = publicWidget.Widget.extend({
    selector: '.o_portal_sale_sidebar',
    events: {
        'change #legal_accept': '_onChangeLegalAccepted',
        'click a[data-bs-target="#modalaccept"]': '_onClickConfirmBtn',
    },

    start() {
        this.legalAccepted = false;
        this.legalAcceptedCheckbox = this.el.querySelector('#legal_accept');
        if (this.legalAcceptedCheckbox) {
            this.legalAccepted = this.legalAcceptedCheckbox.checked;
        }
        $('#modalaccept').on('show.bs.modal', (event) => {
            if (!this.legalAccepted) {
                event.preventDefault();
            }
        });
        return this._super(...arguments);
    },

    _onChangeLegalAccepted(event) {
        event.target.classList.remove(HIGHLIGHT_CLASS);
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
            this.legalAccepted = data;
        }).guardedCatch((error) => {
            event.target.checked = !checked;
        });
    },

    _onClickConfirmBtn: function (event) {
        if (!this.legalAccepted && this.legalAcceptedCheckbox) {
            this.legalAcceptedCheckbox.classList.add(HIGHLIGHT_CLASS);
        }
    },
});
