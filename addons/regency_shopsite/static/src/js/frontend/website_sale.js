odoo.define('regency_shopsite.website_sale', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');


    publicWidget.registry.ReorderCart = publicWidget.Widget.extend({
        selector: '.card-body',
        events: {
            'click #reorder': '_onСlickReorder',
            'click .reorder_line': '_onСlickReorderLine',
        },

        _onСlickReorder(ev) {
            let _t = this;
            $('.reorder_line').each(function (){
                _t._rpc({
                    route: "/shop/cart/reorder",
                    params: {
                        sale_order_line_id: parseInt(this.dataset.lineId)
                    },
                }).then(function (resp) {
                    $('.my_cart_quantity').html(resp.cart_quantity || '<i class="fa fa-warning" /> ');

                })
            });

        },

        _onСlickReorderLine(ev) {
            this._rpc({
                route: "/shop/cart/reorder",
                params: {
                    sale_order_line_id: parseInt(ev.target.dataset.lineId)
                },
            }).then(function (resp) {
                 $('.my_cart_quantity').html(resp.cart_quantity || '<i class="fa fa-warning" /> ');

            })
        },

    });
});