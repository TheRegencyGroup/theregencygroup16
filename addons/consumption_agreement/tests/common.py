from odoo.addons.sale.tests.common import TestSaleCommon
from odoo import Command


class TestConsumptionCommon(TestSaleCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        warehouse = cls.env['stock.warehouse'].search([('company_id', '=', cls.company_data['company'].id)])
        warehouse.mto_mts_management = True
        mto_mts = cls.env.ref('stock_mts_mto_rule.route_mto_mts')
        buy_route = cls.env.ref('purchase_stock.route_warehouse0_buy')

        vendor = cls.env['res.partner'].create({
            'name': 'Super Vendor'
        })

        product = cls.env['product.product'].create({
            'name': 'SuperProduct',
            'type': 'product',
            'route_ids': [(6, 0, (mto_mts + buy_route).ids)],
            'seller_ids': [(0, 0, {
                'partner_id': vendor.id,
            })],
        })
        cls.consumption = cls.env['consumption.agreement'].with_context(tracking_disable=True).create({
            'partner_id': cls.partner_a.id,
            'line_ids': [
                Command.create({
                    'product_id': product.id,
                    'qty_allowed': 1000,
                    'price_unit': 0.1,
                    'vendor_id': vendor.id
                })
            ]
        })
        cls.context_ca = {
            'active_model': 'consumption.agreement',
            'active_ids': [cls.consumption.id],
            'active_id': cls.consumption.id
        }