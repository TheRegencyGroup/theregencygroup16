odoo.define('consumption_agreement.consumption_agreement_portal', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');


    publicWidget.registry.ConsumptionAgreementPortal = publicWidget.Widget.extend({
        selector: '.o_portal_sale_sidebar',
        events: {
            'click #create_sale_order_button': 'async _onClickCreateSaleOrder',
            'click #accept_sign': '_onClickModalOpen',
            'click #decline_sign': '_onClickModalHide',
        },

        async start() {
            await this._super(...arguments);
            this.orderDetail = this.$el.find('table#consumption_table').data();
        },

        /**
         * Process the change in line quantity
         *
         * @private
         * @param {Event} ev
         */
        _onClickCreateSaleOrder(ev) {
            ev.preventDefault();

            let self = this,
                selected_ids = $('td#selection input:checked').map(function () {
                    return $(this).attr("select-id");
                }).get();

            return this._callCreateOrder(self.orderDetail.orderId, {
                'selected_line_ids': selected_ids,
                'access_token': self.orderDetail.token
            }).then(function (data) {
                if (data.error) {
                    self.$('.o_portal_sign_error_msg').remove();
                    self.$controls.prepend(qweb.render('portal.portal_signature_error', { widget: data }));
                } else if (data.success) {
                    var $success = qweb.render('portal.portal_signature_success', { widget: data });
                    self.$el.empty().append($success);
                }
                if (data.force_refresh) {
                    if (data.redirect_url) {
                        window.location = data.redirect_url;
                    } else {
                        window.location.reload();
                    }
                    // no resolve if we reload the page
                    return new Promise(function () {
                    });
                }
            });
        },

        /**
         * Calls the route to get updated values of the line and order
         * when the quantity of a product has changed
         *
         * @private
         * @param {integer} order_id
         * @param {Object} params
         * @return {Deferred}
         */
        _callCreateOrder(order_id, params) {
            return this._rpc({
                route: "/my/consumptions/" + order_id + "/create_sale_order",
                params: params,
            });
        },

        _onClickModalOpen: function (ev) {
            $('#modalaccept_consumption').modal('show')
        },

        _onClickModalHide: function (ev) {
            $('#modalaccept_consumption').modal('hide')
        }

    })


});
