odoo.define('regency_estimate.price_sheet_portal', function (require) {
'use strict';

var publicWidget = require('web.public.widget');

publicWidget.registry.PortalHomeCounters.include({
        /**
         * @override
         */
        _getCountersAlwaysDisplayed() {
            return this._super(...arguments).concat(['price_sheets_count']);
        },
    });

publicWidget.registry.PriceSheetPortal = publicWidget.Widget.extend({
    selector: '.o_portal_sale_sidebar',
    events: {
        'click #create_sale_order_from_price_sheet_button': 'async _onClickCreateSaleOrderFromPriceSheet',
        'click #create_consumption_from_price_sheet_button': 'async _onClickCreateConsumptionAgreementFromPriceSheet',
        'change .js_price_sheet_selection_type': '_onChangeType',
        'change .js_price_sheet_quantity': '_onChangeQuantity',
        'click a.js_update_price_sheet_line_json': '_onClick',
    },

    async start() {
        await this._super(...arguments);
        this.orderDetail = this.$el.find('table#price_sheet_table').data();
        this.elems = this._getUpdatableElements();
    },

     /**
     * Process the change in line quantity
     *
     * @private
     * @param {Event} ev
     */
    async _onClickCreateSaleOrderFromPriceSheet(ev) {
        ev.preventDefault();

        let self = this;
        let selected_ids = $('td#selection input:checked').map(function(){return $(this).attr("select-id");}).get();

        return this._callCreateOrder(self.orderDetail.orderId, {
            'selected_line_ids': selected_ids,
            'access_token': self.orderDetail.token
        }).then(function (data) {
            if (data.error) {
                self.$('.o_portal_sign_error_msg').remove();
            } else if (data.success) {
                var $success = qweb.render('portal.portal_signature_success', {widget: data});
                self.$el.empty().append($success);
            }
            if (data.force_refresh) {
                if (data.redirect_url) {
                    window.location = data.redirect_url;
                } else {
                    window.location.reload();
                }
                // no resolve if we reload the page
                return new Promise(function () { });
            }
        })
    },

    /**
     * Process the change in line quantity
     *
     * @private
     * @param {Event} ev
     */
    async _onClickCreateConsumptionAgreementFromPriceSheet(ev) {
        ev.preventDefault();

        let self = this;
        let selected_ids = $('td#selection input:checked').map(function(){return $(this).attr("select-id");}).get();

        return this._callCreateConsumptionAgreement(self.orderDetail.orderId, {
            'selected_line_ids': selected_ids,
            'access_token': self.orderDetail.token
        }).then(function (data) {
            if (data.error) {
                self.$('.o_portal_sign_error_msg').remove();
            } else if (data.success) {
                var $success = qweb.render('portal.portal_signature_success', {widget: data});
                self.$el.empty().append($success);
            }
            if (data.force_refresh) {
                if (data.redirect_url) {
                    window.location = data.redirect_url;
                } else {
                    window.location.reload();
                }
                // no resolve if we reload the page
                return new Promise(function () { });
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
            route: "/my/price_sheets/" + order_id + "/create_sale_order",
            params: params,
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
    _callCreateConsumptionAgreement(order_id, params) {
        return this._rpc({
            route: "/my/price_sheets/" + order_id + "/create_consumption_agreement",
            params: params,
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
    _callUpdateLineRoute(order_id, params) {
        return this._rpc({
            route: "/my/price_sheets/" + order_id + "/update_line_dict",
            params: params,
        });
    },
    /**
     * Processes data from the server to update the orderline UI
     *
     * @private
     * @param {Element} $orderLine: orderline element to update
     * @param {Object} data: contains order and line updated values
     */
    _updateOrderLineValues($orderLine, data) {
        let linePriceSubTotal = data.order_line_price_subtotal,
            linePortalFee = data.order_line_portal_fee,
            $linePortalFee = $orderLine.find('.oe_order_line_portal_fee'),
            $linePriceSubTotal = $orderLine.find('.oe_order_line_price_subtotal .oe_currency_value');

        $orderLine.find('.js_price_sheet_quantity').val(data.order_line_product_uom_qty);
        if ($linePriceSubTotal.length && linePriceSubTotal !== undefined) {
            $linePriceSubTotal.text(linePriceSubTotal);
        }
        if ($linePortalFee.length && linePortalFee !== undefined) {
            $linePortalFee.text(linePortalFee);
        }
    },
    /**
     * Processes data from the server to update the UI
     *
     * @private
     * @param {Object} data: contains order and line updated values
     */
    _updateOrderValues(data) {
        let orderAmountTotal = data.order_amount_total,
            orderAmountUntaxed = data.order_amount_untaxed,
            // orderAmountUndiscounted = data.order_amount_undiscounted,
            $orderTotalsTable = $(data.order_totals_table);
        // if (orderAmountUntaxed !== undefined) {
        //     this.elems.$orderAmountUntaxed.text(orderAmountUntaxed);
        // }

        // if (orderAmountTotal !== undefined) {
        //     this.elems.$orderAmountTotal.text(orderAmountTotal);
        // }

        // if (orderAmountUndiscounted !== undefined) {
        //     this.elems.$orderAmountUndiscounted.text(orderAmountUndiscounted);
        // }
        if ($orderTotalsTable.length) {
            this.elems.$orderTotalsTable.find('table').replaceWith($orderTotalsTable);
        }
    },
    /**
     * Locate in the DOM the elements to update
     * Mostly for compatibility, when the module has not been upgraded
     * In that case, we need to fall back to some other elements
     *
     * @private
     * @return {Object}: Jquery elements to update
     */
    _getUpdatableElements() {
        // let $orderAmountUntaxed = $('[data-id="total_untaxed"]').find('span, b'),
        //     $orderAmountTotal = $('[data-id="total_amount"]').find('span, b'),
        //     $orderAmountUndiscounted = $('[data-id="amount_undiscounted"]').find('span, b');
        //
        // if (!$orderAmountUntaxed.length) {
        //     $orderAmountUntaxed = $orderAmountTotal.eq(1);
        //     $orderAmountTotal = $orderAmountTotal.eq(0).add($orderAmountTotal.eq(2));
        // }

        return {
            // $orderAmountUntaxed: $orderAmountUntaxed,
            // $orderAmountTotal: $orderAmountTotal,
            $orderTotalsTable: $('#total'),
            // $orderAmountUndiscounted: $orderAmountUndiscounted,
        };
    },

     /**
     * Process the change in line quantity
     *
     * @private
     * @param {Event} ev
     */
    _onChangeQuantity(ev) {
        ev.preventDefault();
        let self = this,
            $target = $(ev.currentTarget),
            quantity = parseInt($target.val());

        this._callUpdateLineRoute(self.orderDetail.orderId, {
            'line_id': $target.data('lineId'),
            'input_quantity': quantity >= 0 ? quantity : false,
            'access_token': self.orderDetail.token
        }).then((data) => {
            self._updateOrderLineValues($target.closest('tr'), data);
            self._updateOrderValues(data);
        });
    },
    /**
     * Reacts to the click on the -/+ buttons
     *
     * @param {Event} ev
     */
    _onClick(ev) {
        ev.preventDefault();
        let self = this,
            $target = $(ev.currentTarget);
        this._callUpdateLineRoute(self.orderDetail.orderId, {
            'line_id': $target.data('lineId'),
            'remove': $target.data('remove'),
            'unlink': $target.data('unlink'),
            'access_token': self.orderDetail.token
        }).then((data) => {
            var $saleTemplate = $(data['price_sheet_template']);
            if ($saleTemplate.length && data['unlink']) {
                self.$('#portal_sale_content').html($saleTemplate);
                self.elems = self._getUpdatableElements();
            }
            self._updateOrderLineValues($target.closest('tr'), data);
            self._updateOrderValues(data);
        });
    },
     /**
     * Process the change in line quantity
     *
     * @private
     * @param {Event} ev
     */
    _onChangeType(ev) {
        ev.preventDefault();
        let self = this,
            $target = $(ev.currentTarget),
            value = $target[0].value;

        this._callUpdateLineType(self.orderDetail.orderId, {
            'line_id': $target.data('lineId'),
            'consumption_type': value,
            'access_token': self.orderDetail.token
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
    _callUpdateLineType(order_id, params) {
        return this._rpc({
            route: "/my/price_sheets/" + order_id + "/update_line_type",
            params: params,
        });
    },
});

});
