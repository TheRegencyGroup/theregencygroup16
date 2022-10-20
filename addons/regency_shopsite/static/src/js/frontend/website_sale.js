odoo.define('regency_shopsite.website_sale', function (require) {
    'use strict';

    const PublicWidget = require('web.public.widget');

    PublicWidget.registry.ReorderCart = PublicWidget.Widget.extend({
        selector: '.card-body',
        events: {
            'click #reorder': '_onClickReorder',
            'click .reorder_line': '_onClickReorderLine',
        },

        _onClickReorder(ev) {
            let that = this;
            $('.reorder_line').each(function () {
                that._rpc({
                    route: "/shop/cart/reorder",
                    params: {
                        sale_order_line_id: parseInt(this.dataset.lineId)
                    },
                }).then(function (resp) {
                    $('.my_cart_quantity').html(resp.cart_quantity || '<i class="fa fa-warning"/> ');

                })
            });

        },

        _onClickReorderLine(ev) {
            this._rpc({
                route: "/shop/cart/reorder",
                params: {
                    sale_order_line_id: parseInt(ev.target.dataset.lineId)
                },
            }).then(function (resp) {
                $('.my_cart_quantity').html(resp.cart_quantity || '<i class="fa fa-warning"/> ');
            })
        },
    });
});