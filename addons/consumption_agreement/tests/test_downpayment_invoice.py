from odoo.tests import tagged, Form
from odoo.addons.sale.tests.common import TestSaleCommon
from odoo import Command


@tagged('all_run', 'post_install')
class TestDownpayment(TestSaleCommon):

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
                    'price_unit': 0.1
                })
            ]
        })
        cls.context_ca = {
            'active_model': 'consumption.agreement',
            'active_ids': [cls.consumption.id],
            'active_id': cls.consumption.id
        }

    def test_create_downpayment_for_ca(self):
        self.consumption.action_confirm()
        self.assertEqual(0, self.consumption.invoice_count)
        self.assertEqual(100, self.consumption.tax_totals.get('amount_total'))

        downpayment = self.env['sale.advance.payment.inv'].with_context(self.context_ca).create({
            'advance_payment_method': 'percentage',
            'amount': 10,
        })
        downpayment.create_invoices()
        self.assertEqual(1, self.consumption.invoice_count)
        self.assertEqual(10, self.consumption.deposit_percent)
        downpayment = self.env['sale.advance.payment.inv'].with_context(self.context_ca).create({
            'advance_payment_method': 'percentage',
            'amount': 5,
        })
        downpayment.create_invoices()
        self.assertEqual(2, self.consumption.invoice_count)
        self.assertEqual(15, self.consumption.deposit_percent)

        # Create SO from CA:

        res = self.consumption.action_create_so()
        wiz = self.env['sale.order.ca.wizard'].browse(res.get('res_id'))
        wiz.create_so_from_ca()
        self.assertEqual(1, self.consumption.sale_order_count)
        so = self.consumption.sale_order_ids[0]

        # confirm SO and check if Dowmpayment line have been added

        so.action_confirm()
        self.assertEqual(3, len(so.order_line))
        self.assertEqual(2, so.invoice_count)
        dsection = so.order_line[1]
        self.assertEqual('line_section', dsection.display_type)
        self.assertEqual('Down Payments', dsection.name[0:13])
        dline = so.order_line[2]
        self.assertEqual('Down Payment', dline.name[0:12])
        self.assertEqual(2, dline.qty_invoiced)  # we have 2 downpayment invoices
        self.assertEqual(100 * 0.15, dline.price_unit * dline.qty_invoiced)

        # process product from Receipt to Delivery in order to invoice SO
        purchase_order_ids = so._get_purchase_orders()
        purchase_order_ids.button_confirm()
        picking = purchase_order_ids.picking_ids[0]
        res = picking.button_validate()
        Form(self.env[res['res_model']].with_context(res['context'])).save().process()
        picking = so.picking_ids[0]
        res = picking.button_validate()
        Form(self.env[res['res_model']].with_context(res['context'])).save().process()
        self.assertEqual('to invoice', so.invoice_status)

        # create regular invoice for SO
        context = { 'active_model': 'sale.order',
                    'active_ids': [so.id],
                    'active_id': so.id,
                    'default_advance_payment_method': 'delivered'}
        downpayment = self.env['sale.advance.payment.inv'].with_context(context).create({
            'advance_payment_method': 'delivered'
        })
        downpayment.create_invoices()
        self.assertEqual(100, so.tax_totals.get('amount_total'))
        self.assertEqual(3, so.invoice_count)
        invoice = so.invoice_ids.sorted('id')[2]
        self.assertEqual(100 - 100 * 0.15, invoice.tax_totals.get('amount_total'))


